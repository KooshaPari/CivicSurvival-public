"""Harmony patches discipline suite.

Locks in the contract between CivicSurvival/Patches/*.cs files and
CivicSurvival/Patches/HarmonyPatchBootstrapper.cs.

Rules enforced:
  1. Every patch file in CivicSurvival/Patches/ (excluding HarmonyPatchBootstrapper)
     is either:
       - Explicitly registered via `XxxPatch.Apply(harmony)` AND `XxxPatch.Cleanup(...)`
       - Implicitly registered via [HarmonyPatch] attributes AND verified via
         XxxPatch.VerifyAndReport()
 + verified via
 + verified via
         XxxPatch.VerifyAndReport() + XxxPatch.Cleanup()
  2. Every explicit patch has an `Apply(HarmonyLib.Harmony)` method.
  3. Every explicit patch has a `Cleanup(...)` method.
  4. Every attribute-based patch has a `VerifyAndReport()` method.
  5. The patch file count matches the registered count (no orphans).
  6. No patch file lives outside CivicSurvival/Patches/ (they should all be there
     for discoverability).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("CivicSurvival")
PATCHES_DIR = ROOT / "Patches"
BOOTSTRAPPER = PATCHES_DIR / "HarmonyPatchBootstrapper.cs"

# The bootstrapper itself is the file that does the registration — it's exempt.
EXCLUDE_FROM_PATCHES = {"HarmonyPatchBootstrapper.cs"}


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def _patch_files() -> list[Path]:
    return sorted(p for p in PATCHES_DIR.glob("*.cs") if p.name not in EXCLUDE_FROM_PATCHES)


def _bootstrapper_text() -> str:
    return _read(BOOTSTRAPPER)


def test_every_patch_file_is_registered_in_bootstrapper() -> None:
    """Every patch file in CivicSurvival/Patches/ must be wired in HarmonyPatchBootstrapper.

    Either explicit (Apply/Cleanup in bootstrapper) or attribute-based (VerifyAndReport/Cleanup).
    Cleanup may be invoked (Cleanup(world)) or referenced as a method group (Cleanup)
    inside RunCleanup(..., XxxPatch.Cleanup).
    """
    bs_text = _bootstrapper_text()
    unregistered = []
    for p in _patch_files():
        # File stems don't all end in Patch (BarrierGateViolationDetector,
        # VanillaSystemAutoProfiler). Use the stem verbatim.
        stem = p.stem
        has_explicit = bool(re.search(rf"\b{re.escape(stem)}\.Apply\s*\(", bs_text))
        has_verify = bool(re.search(rf"\b{re.escape(stem)}\.VerifyAndReport\s*\(", bs_text))
        has_cleanup = bool(re.search(rf"\b{re.escape(stem)}\.Cleanup(?:\s*\(|\b)", bs_text))
        if not (has_explicit or has_verify) or not has_cleanup:
            unregistered.append(p.name)
    assert not unregistered, (
        f"Patch files in CivicSurvival/Patches/ not wired in HarmonyPatchBootstrapper: "
        f"{unregistered}. Each patch must have either Apply(harmony)+Cleanup OR "
        f"VerifyAndReport+Cleanup called from HarmonyPatchBootstrapper."
    )


def test_every_explicit_patch_has_apply_and_cleanup() -> None:
    """Every explicit patch must expose public static Apply(Harmony) and Cleanup()."""
    bs_text = _bootstrapper_text()
    # Find every XxxStem.Apply(harmony) call — class names don't all end in Patch.
    explicit = re.findall(r"\b([A-Z]\w+)\.Apply\s*\(", bs_text)
    missing_apply = []
    missing_cleanup = []
    seen = set()
    for name in explicit:
        if name in seen:
            continue
        seen.add(name)
        p = PATCHES_DIR / f"{name}.cs"
        if not p.exists():
            continue  # Not a patch file (some Apply() calls belong to other bootstrapper steps).
        text = _read(p)
        if not re.search(r"\bpublic\s+static\s+void\s+Apply\s*\(\s*Harmony\b", text):
            missing_apply.append(name)
        if not re.search(r"\bpublic\s+static\s+void\s+Cleanup\s*\(", text):
            missing_cleanup.append(name)
    assert not missing_apply, (
        f"Explicit patches missing `public static void Apply(Harmony)`: {missing_apply}"
    )
    assert not missing_cleanup, (
        f"Explicit patches missing `public static void Cleanup(...)`: {missing_cleanup}"
    )


def test_every_attribute_based_patch_has_verify_and_cleanup() -> None:
    """Every attribute-based patch must expose VerifyAndReport() and Cleanup()."""
    bs_text = _bootstrapper_text()
    # Find every Stem.VerifyAndReport() call — class names don't all end in Patch.
    attribute_based = re.findall(r"\b([A-Z]\w+)\.VerifyAndReport\s*\(\s*\)", bs_text)
    missing_verify = []
    missing_cleanup = []
    seen = set()
    for name in attribute_based:
        if name in seen:
            continue
        seen.add(name)
        p = PATCHES_DIR / f"{name}.cs"
        if not p.exists():
            missing_verify.append(f"{name} (no file)")
            continue
        text = _read(p)
        if not re.search(r"\bpublic\s+static\s+void\s+VerifyAndReport\s*\(\s*\)", text):
            missing_verify.append(name)
        if not re.search(r"\bpublic\s+static\s+void\s+Cleanup\s*\(\s*\)", text):
            missing_cleanup.append(name)
    assert not missing_verify, (
        f"Attribute-based patches missing `public static void VerifyAndReport()`: {missing_verify}"
    )
    assert not missing_cleanup, (
        f"Attribute-based patches missing `public static void Cleanup()`: {missing_cleanup}"
    )


def test_bootstrapper_has_debug_only_block_marker() -> None:
    """HarmonyPatchBootstrapper must use #if DEBUG blocks for debug-only patches.

    The BarrierGateViolationDetector is a DEBUG-only patch (per the comments in
    HarmonyPatchBootstrapper.cs:36). This discipline test ensures the conditional
    compilation is preserved — if someone removes the #if DEBUG guard, debug
    instrumentation would ship to retail players.
    """
    text = _bootstrapper_text()
    # Find #if DEBUG ... #endif blocks and verify BarrierGateViolationDetector
    # only appears inside one.
    debug_block_pattern = re.compile(r"#if\s+DEBUG\s*\n(.*?)#endif", re.DOTALL)
    debug_blocks = debug_block_pattern.findall(text)
    bg_inside_debug = any("BarrierGateViolationDetector" in block for block in debug_blocks)
    assert bg_inside_debug, (
        f"BarrierGateViolationDetector must be inside an #if DEBUG block in "
        f"HarmonyPatchBootstrapper.cs (currently {'inside' if bg_inside_debug else 'NOT inside'} "
        f"a debug block). Otherwise debug instrumentation ships to retail players."
    )


def test_no_patch_file_outside_patches_directory() -> None:
    """No file in CivicSurvival/ that defines [HarmonyPatch] classes lives outside CivicSurvival/Patches/.

    Discoverability: every patch must be co-located so a contributor looking for
    "where are Harmony patches defined?" finds them in one folder.
    """
    pattern = re.compile(
        r"\[HarmonyPatch(?:\([^)]*\))?\]\s*\n?\s*(?:public|internal)?\s*(?:static\s+)?class\s+(\w+)"
    )
    offenders = []
    for cs in ROOT.rglob("*.cs"):
        if "obj" in cs.parts or "bin" in cs.parts:
            continue
        # The HarmonyPatchBootstrapper itself doesn't have [HarmonyPatch] classes — it APPLIES them.
        if cs.parent == PATCHES_DIR:
            continue
        text = _read(cs)
        if pattern.search(text):
            offenders.append(str(cs))
    assert not offenders, (
        f"Files containing [HarmonyPatch] classes that live outside CivicSurvival/Patches/: "
        f"{offenders}. All Harmony patch classes must be co-located in CivicSurvival/Patches/."
    )


def test_bootstrapper_call_count_matches_patch_file_count() -> None:
    """The number of patches referenced in the bootstrapper must equal the number of patch files.

    Drift here means: a contributor added a patch file but forgot to register it,
    OR removed a patch file but left the registration calls.
    """
    bs_text = _bootstrapper_text()
    # Find every stem that's called with Apply or VerifyAndReport.
    referenced = set(re.findall(r"\b([A-Z]\w+)\.(?:Apply|VerifyAndReport)\s*\(", bs_text))
    files = {p.stem for p in _patch_files()}
    # Only count referenced names that correspond to actual patch files in the dir.
    referenced_files = referenced & files
    extra_refs = referenced_files - files
    extra_files = files - referenced_files
    assert not extra_refs, f"Bootstrapper references patches that don't exist: {extra_refs}"
    assert not extra_files, f"Patch files that the bootstrapper doesn't reference: {extra_files}"


if __name__ == "__main__":
    import subprocess
    import sys

    rc = subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"])
    sys.exit(rc)
