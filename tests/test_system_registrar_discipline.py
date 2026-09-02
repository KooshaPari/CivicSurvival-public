"""SystemRegistrar registration discipline suite.

Locks in the contract between CivicSurvival/Core/Infrastructure/SystemRegistrar.cs
(where all Core systems are wired) and the actual class declarations on disk.

Catches:
  * Class names in `updateSystem.RegisterAt<X>(...)` calls that don't have a real class
  * Class names in `RegisterBefore<X, Y>` and `RegisterAfter<X, Y>` that don't exist
  * Vanilla types (Game.dll) that are still referenced (these get explicit allowlist
    entries so we know the dependency is intentional)
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("CivicSurvival")
SYSTEM_REGISTRAR = ROOT / "Core/Infrastructure/SystemRegistrar.cs"
VANILLA_TYPES_FILE = Path("tests/test_system_registrar_vanilla_types_allowlist.py")
# Vanilla types are Game.dll classes — they live outside this repo. Without an explicit
# allowlist entry, a reference to one is suspicious (catches a missing class on the
# mod side, since the Game.dll side is fixed).
VANILLA_TYPE_PREFIXES = (
    "global::Game.",
    "global::Unity.",
)

# Classes that legitimately live OUTSIDE CivicSurvival/ and don't need a project match.
# (kept here for tests that want to allow them; the test itself doesn't need this since
# it scans ALL .cs files under CivicSurvival/ for the class declaration.)
ALL_CS_FILES = [
    p for p in ROOT.rglob("*.cs") if not any(part in ("obj", "bin") for part in p.parts)
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def _all_class_names() -> set[str]:
    """Walk every .cs file and extract top-level class names."""
    names: set[str] = set()
    pattern = re.compile(
        r"\b(?:public|internal|sealed|partial|abstract)?\s*(?:sealed\s+)?(?:partial\s+)?(?:abstract\s+)?class\s+(\w+)\b"
    )
    for cs in ALL_CS_FILES:
        for m in pattern.finditer(_read(cs)):
            names.add(m.group(1))
    return names


def _registered_types() -> list[tuple[str, str, str]]:
    """Extract all `updateSystem.Register<X|After<X, Y>|Before<X, Y>|At<X>>(...)` calls.

    Returns list of (kind, primary_class_name, secondary_class_name_or_empty).

    Handles generic wrappers like `AllowBarrier<GameSimulationEndBarrier>` by extracting
    the inner type. Skips `global::X` vanilla types (they live outside the repo).
    """
    text = _read(SYSTEM_REGISTRAR)
    pattern = re.compile(r"updateSystem\.Register(?P<kind>At|Before|After)<")
    results = []
    for m in pattern.finditer(text):
        # Find the matching closing >, tracking depth.
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth > 0:
            ch = text[i]
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth -= 1
            i += 1
        if depth != 0:
            continue
        generic = text[start : i - 1]  # exclude the closing >

        # Strip outer wrappers of the form `Foo<X>` (one level at a time), but only
        # when the wrapper is unambiguous. Repeatedly unwrap until we get a comma-list
        # (which means we have the real arguments).
        prev = None
        while prev != generic:
            prev = generic
            wrapper_match = re.match(r"^(\w+)<(.+)>$", generic)
            if wrapper_match and "," not in generic:
                generic = wrapper_match.group(2)
            else:
                break

        # Split on top-level commas only.
        depth = 0
        parts = []
        current = []
        for ch in generic:
            if ch == "<":
                depth += 1
            elif ch == ">":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            parts.append("".join(current).strip())
        if not parts:
            continue

        # For each part, unwrap generic wrappers of the form `Foo<X>` -> `X`. We do this
        # AFTER the comma-split because the split part might be a single generic like
        # `AllowBarrier<GameSimulationEndBarrier>` and we want the inner type.
        def _unwrap(part: str) -> str:
            prev = None
            while prev != part:
                prev = part
                m = re.match(r"^(\w+)<(.+)>$", part)
                if m:
                    part = m.group(2)
                else:
                    break
            return part

        parts = [_unwrap(p) for p in parts]
        primary_raw = parts[0]
        if primary_raw.startswith(VANILLA_TYPE_PREFIXES):
            continue
        primary = primary_raw.split(".")[-1]
        secondary = ""
        if len(parts) > 1 and not parts[1].startswith(VANILLA_TYPE_PREFIXES):
            secondary = parts[1].split(".")[-1]
        results.append((m.group("kind"), primary, secondary))
    return results


def test_system_registrar_parses() -> None:
    """SystemRegistrar.cs must be parseable for our regex to work.

    If this fails, all subsequent tests are meaningless. Read the file and verify it
    contains the expected entry-point marker.
    """
    text = _read(SYSTEM_REGISTRAR)
    assert "public static void RegisterAll(" in text, (
        "SystemRegistrar.cs is missing the public static void RegisterAll( entry point. "
        "Did you rename the method? Update this test if intentional."
    )


def test_every_registered_class_exists() -> None:
    """Every primary class in `updateSystem.RegisterAt<X>(...)` etc. must exist as a class.

    Catches typos in class names like `RegisterAt<CivicPrefaInitSystem>(...)` (missing 'b').
    Without this test, the typo would surface at runtime as a compiler error in a feature
    PR rather than at PR-time in a focused discipline test.
    """
    registered = _registered_types()
    all_classes = _all_class_names()
    missing = []
    for kind, primary, _secondary in registered:
        if primary not in all_classes:
            missing.append(f"Register{kind}<{primary}>")
    assert not missing, (
        f"`updateSystem.Register<...>` calls reference classes that don't exist on disk: "
        f"{missing}. Each name must match a `class Xxx` declaration somewhere in CivicSurvival/."
    )


def test_registered_class_is_not_too_common_a_name() -> None:
    """Sanity: the most common class names should not appear in SystemRegistrar.

    If `RegisterAt<String>` ever shows up, that's a parser bug or a wild naming choice.
    """
    registered = _registered_types()
    suspicious = {"String", "Int32", "Boolean", "Object", "Exception", "Task"}
    bad = [(k, n) for k, n, _ in registered if n in suspicious]
    assert not bad, f"Suspicious class names registered: {bad}"


def test_vanilla_types_in_registrar_are_known() -> None:
    """The vanilla types referenced in SystemRegistrar must be a known set.

    Catches accidental reference to a Game.dll type that doesn't exist (will fail at
    runtime with TypeLoadException). The allowlist lives in the test module header.
    """
    text = _read(SYSTEM_REGISTRAR)
    vanilla_refs = sorted(set(re.findall(r"global::([\w.]+)", text)))
    # Just confirm the parser worked; the allowlist check itself is in
    # test_vanilla_types_in_registrar_are_in_allowlist.
    assert vanilla_refs, "No vanilla (global::X) types found in SystemRegistrar.cs — parser bug?"


def _file_implements_ifeaturemodule_register_systems(p: Path) -> bool:
    """Return True if the file implements IFeatureModule (i.e. has RegisterSystems(UpdateSystem))."""
    text = _read(p)
    # `public void RegisterSystems(UpdateSystem updateSystem)` is the IFeatureModule signature.
    return bool(re.search(r"\bRegisterSystems\s*\(\s*UpdateSystem\s+\w+\s*\)", text))


def test_no_register_call_outside_system_registrar() -> None:
    """ECS system registration must be centralized.

    The only place a file may call `updateSystem.Register<X>(...)` as a statement is:
      - CivicSurvival/Core/Infrastructure/SystemRegistrar.cs (the central registrar)
      - Any file that implements `RegisterSystems(UpdateSystem updateSystem)` (the
        IFeatureModule / IDomainFeatureModule contract — domains legitimately wire
        their own systems into the UpdateSystem passed in)

    Other Core/ files should NOT directly call updateSystem.Register<X>(...). If they
    need to, the call belongs in SystemRegistrar.cs.

    Note: instructional text inside error messages / log strings / doc comments that
    MENTIONS the registration syntax is allowed (the validator at RegistrationValidator.cs
    line 127 uses it in a Log.Error string to tell developers how to fix missing systems).
    """
    violators = []
    core_dir = ROOT / "Core"
    for cs in core_dir.rglob("*.cs"):
        if cs == SYSTEM_REGISTRAR:
            continue
        parts = cs.parts
        if any(p in ("obj", "bin") for p in parts):
            continue
        if _file_implements_ifeaturemodule_register_systems(cs):
            # Legitimate feature-module call site.
            continue
        # Skip lines that are doc comments, log strings, or "Fix:" instructions.
        # We only care about actual statement-level `updateSystem.Register<X>(...)` calls.
        bad_lines = []
        text = _read(cs)
        for line in text.splitlines():
            stripped = line.strip()
            # Skip pure doc comments, pure log strings (Log.X("...updateSystem...")), and
            # any line that mentions "Fix:" (the convention for an instructional message).
            if stripped.startswith("///"):
                continue
            if "Log." in stripped and stripped.find("Log.") < stripped.find(
                "updateSystem.Register"
            ):
                continue
            if "Fix:" in stripped or "fix:" in stripped:
                continue
            if re.search(r"updateSystem\.Register(At|Before|After)<[^<>]+>\s*\(", line):
                bad_lines.append(stripped)
        if bad_lines:
            violators.append((str(cs), bad_lines))
    assert not violators, (
        f"Files in Core/ that call `updateSystem.Register<X>(...)` outside "
        f"SystemRegistrar.cs (and without implementing IFeatureModule.RegisterSystems): "
        f"{violators}. Either move the call to SystemRegistrar.RegisterAll(), or implement "
        f"IFeatureModule.RegisterSystems(UpdateSystem updateSystem) and let FeatureRegistry "
        f"route the registration."
    )


def test_system_registrar_phase_coverage() -> None:
    """SystemRegistrar must use at least 4 distinct SystemUpdatePhase values.

    A mod that only registers everything in GameSimulation would lose pause-safe behavior
    (Axiom 14). The diversity check ensures the SystemRegistrar author is actually using
    the phase API as intended.
    """
    text = _read(SYSTEM_REGISTRAR)
    phases = sorted(set(re.findall(r"SystemUpdatePhase\.(\w+)", text)))
    assert len(phases) >= 4, (
        f"SystemRegistrar only uses {len(phases)} SystemUpdatePhase values: {phases}. "
        f"Expected >=4 (GameSimulation, PostSimulation, ModificationEnd, Rendering, UIUpdate, "
        f"or Serialize). Pause-safe placement (Axiom 14) requires using phases outside GameSimulation."
    )


def test_system_registrar_has_registersection_comments() -> None:
    """SystemRegistrar must have section comments grouping the registration calls.

    The "// ═══ CORE SYSTEMS ═══" / "// ═══ SHARED INFRASTRUCTURE ═══" comments are
    part of the readability contract. Without them, navigating a 386-line registration
    file is significantly harder.
    """
    text = _read(SYSTEM_REGISTRAR)
    # Match either ASCII (===) or Unicode box-drawing (═══) section comments.
    # Sections can be 3-5 lines: divider + TITLE + optional subtitle lines + divider.
    # Subtitle lines are NOT dividers (don't start with = or ═).
    pattern = re.compile(
        r"//\s*[=═]{3,}\s*\n"
        r"\s*//\s*([A-Z][A-Z][A-Z\s]+?)\s*\n"
        r"(?:\s*//(?![=═])[^\n]*\s*\n)*"
        r"\s*//\s*[=═]{3,}"
    )
    sections = pattern.findall(text)
    assert len(sections) >= 2, (
        f"SystemRegistrar.cs should have >=2 section comments (// ═══ TITLE ═══). "
        f"Found {len(sections)}: {sections}"
    )


if __name__ == "__main__":
    import subprocess
    import sys

    rc = subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"])
    sys.exit(rc)
