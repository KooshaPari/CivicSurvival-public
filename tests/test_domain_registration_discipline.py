"""Domain registration discipline suite.

Locks in the contract between CivicSurvival/Domains/* folders,
CivicSurvival/Mod.cs imports/registrations, and the priority/ADR contract.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("CivicSurvival")
MOD_CS = ROOT / "Mod.cs"
DOMAINS_DIR = ROOT / "Domains"

# Allowlist of *Domain* class names that don't match the folder name verbatim.
# Format: {class_name: folder_name}. Used by tests 3 + 4 to detect drift.
DOMAIN_CLASS_TO_FOLDER = {
    "EconomyDomain": "Economics",  # singular-vs-plural class name vs folder
    "UIDomain": None,              # lives in Services.UI, not a domain folder
    "ArenaUIDomain": None,         # lives in Services.UI/Arena, not a domain folder
    "EffectsDomain": None,         # lives in Core/Systems/Effects, not a domain folder
}

# These features are non-domain Core features that get registered in
# RegisterFeatures() but don't live under CivicSurvival/Domains/.
CORE_FEATURE_ALLOWLIST = {
    "WellbeingFeature",           # Core.Features.Wellbeing
    "PopulationFeature",          # Core.Features.Population
    "DamageAccountingFeature",    # Core.Features.CrossDomain.DamageAccounting
    "ThreatsAirDefenseFeature",   # Core.Features.CrossDomain.ThreatsAirDefense
    "ArenaFeature",               # Services.Arena
    "EfficiencyFeature",          # Core.Features.Efficiency
    "EfficiencyFinalizeFeature",  # Core.Features.Efficiency
}


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def _domain_folders() -> list[str]:
    return sorted(d.name for d in DOMAINS_DIR.iterdir() if d.is_dir())


def _mod_cs_imports() -> list[str]:
    text = _read(MOD_CS)
    return sorted(set(re.findall(r"using\s+CivicSurvival\.Domains\.(\w+);", text)))


def _mod_cs_registers() -> list[str]:
    """Extract `registry.Register(new XxxDomain())` and `registry.Register(new XxxFeature())`."""
    text = _read(MOD_CS)
    domains = sorted(set(re.findall(r"registry\.Register\(new\s+(\w+Domain)\(\)\)", text)))
    features = sorted(set(re.findall(r"registry\.Register\(new\s+(\w+Feature)\(\)\)", text)))
    return domains, features


def test_every_domain_folder_has_mod_cs_import() -> None:
    """Every domain folder on disk must have a `using CivicSurvival.Domains.X;` in Mod.cs."""
    folders = set(_domain_folders())
    usings = set(_mod_cs_imports())
    missing = folders - usings
    assert not missing, (
        f"Domain folder(s) without Mod.cs import: {sorted(missing)}. "
        f"Add `using CivicSurvival.Domains.<Name>;` to Mod.cs."
    )


def test_no_mod_cs_import_without_folder() -> None:
    """Inverse: every `using CivicSurvival.Domains.X;` must point at a real folder."""
    folders = set(_domain_folders())
    usings = set(_mod_cs_imports())
    orphan = usings - folders
    assert not orphan, (
        f"Mod.cs imports for non-existent folder(s): {sorted(orphan)}. "
        f"Either create the folder or remove the using."
    )


def test_every_domain_folder_has_mod_cs_register() -> None:
    """Every domain folder must have a `registry.Register(new XxxDomain())` call.

    Folder name `Xxx` should map to class `XxxDomain`. Exception: `Economics` -> `EconomyDomain`.
    """
    domains_registered, _features = _mod_cs_registers()
    folders = _domain_folders()
    expected_class = {f"{f[:-3]}Domain" if f.endswith("ies") else f"{f}Domain" for f in folders}
    expected_class.discard("EconomicsDomain")  # Economics -> EconomyDomain
    expected_class.add("EconomyDomain")
    registered = set(domains_registered)
    missing = expected_class - registered
    assert not missing, (
        f"Domain folder(s) without `registry.Register(new XxxDomain())`: {sorted(missing)}. "
        f"Add a Register call to Mod.cs::RegisterFeatures()."
    )


def test_no_domain_register_without_folder() -> None:
    """Inverse: every `XxxDomain` registered must come from a real folder.

    Exception: `UIDomain`, `ArenaUIDomain`, `EffectsDomain` live in non-domain namespaces.
    """
    domains_registered, _features = _mod_cs_registers()
    folders = set(_domain_folders())
    registered_class_names = {d[:-6] for d in domains_registered}  # strip 'Domain'
    folder_names = set(folders)
    # Apply the DOMAIN_CLASS_TO_FOLDER mapping (EconomyDomain -> Economics folder).
    expected_folder_names = set()
    for class_name in registered_class_names:
        mapped = DOMAIN_CLASS_TO_FOLDER.get(class_name + "Domain", class_name)
        if mapped is None:
            continue  # Core feature, not a domain
        expected_folder_names.add(mapped)
    # Now: every registered domain class should have a corresponding folder.
    for class_name in registered_class_names:
        mapped = DOMAIN_CLASS_TO_FOLDER.get(class_name + "Domain", class_name)
        if mapped is None:
            continue
        assert mapped in folder_names, (
            f"`registry.Register(new {class_name}Domain())` references missing folder {mapped!r}. "
            f"Either create the folder or remove the register call."
        )


def test_every_domain_class_declares_priority() -> None:
    """Every *Domain.cs file must declare a `PRIORITY = N` constant.

    This is the load-order contract documented in docs/adr/0004-domain-priority-contract.md.
    """
    folders = _domain_folders()
    missing_priority = []
    for f in folders:
        main_file = DOMAINS_DIR / f / f"{f}Domain.cs"
        if not main_file.exists():
            continue
        text = _read(main_file)
        if not re.search(r"PRIORITY\s*=\s*\d+", text):
            missing_priority.append(f"{f} (no PRIORITY constant in {f}Domain.cs)")
    assert not missing_priority, (
        f"Domain(s) missing PRIORITY constant: {missing_priority}. "
        f"Add `public const int PRIORITY = NNNN;` to each Domain.cs file."
    )


def test_no_core_feature_registered_without_definition() -> None:
    """Every `*Feature` register call must resolve to a real class file on disk.

    Detects typos where someone writes `new ArenaFeature()` but the class is actually
    called `ArenaFeatur` or `ArenaFetaure`.
    """
    _domains, features = _mod_cs_registers()
    missing = []
    for fq_class in features:
        # Search any .cs file containing `class {fq_class}` or `class {fq_class} :` etc.
        pattern = re.compile(rf"\bclass\s+{re.escape(fq_class)}\b")
        found = False
        for cs in ROOT.rglob("*.cs"):
            parts = cs.parts
            if any(p in ("obj", "bin") for p in parts):
                continue
            if pattern.search(cs.read_text(encoding="utf-8", errors="ignore")):
                found = True
                break
        if not found:
            missing.append(fq_class)
    assert not missing, (
        f"`registry.Register(new XxxFeature())` calls with no matching class: {sorted(missing)}. "
        f"Either create the class or fix the typo."
    )


def test_domain_count_matches_register_count() -> None:
    """The 28 domain folders should produce 28 Register calls (after allowlists).

    Tests that the contract is stable: if someone adds a domain folder without registering,
    OR registers an orphan without a folder, the counts drift.
    """
    folders = set(_domain_folders())
    domains_registered, _features = _mod_cs_registers()
    # Expected: each folder -> one Domain class (Economics -> EconomyDomain mapping).
    # Plus the 3 Core/Effects/UI domains (UIDomain, ArenaUIDomain, EffectsDomain).
    expected_count = len(folders) + 3  # 28 + 3 = 31
    assert len(domains_registered) == expected_count, (
        f"Expected {expected_count} Register(domain) calls (28 domain folders + "
        f"3 Core: UIDomain, ArenaUIDomain, EffectsDomain), got {len(domains_registered)}. "
        f"Registered: {sorted(domains_registered)}"
    )


def test_domain_priority_values_match_adr_0004() -> None:
    """The PRIORITY values declared in *Domain.cs must match docs/adr/0004.

    This is the test that catches drift in BOTH directions: if someone changes a
    priority in source but not in the ADR, or vice versa.
    """
    adr_path = Path("docs/adr/0004-domain-priority-contract.md")
    if not adr_path.exists():
        # ADR is optional — skip if absent (this test is paired with its own PR).
        return
    adr_text = _read(adr_path)
    # Each domain should appear in the ADR's table as `| Xxx | NNNN |`.
    folders = _domain_folders()
    missing_in_adr = []
    for f in folders:
        class_name = f"{f}Domain" if not f.endswith("ies") else f"{f[:-3]}Domain"
        # Find PRIORITY value in source
        main_file = DOMAINS_DIR / f / f"{f}Domain.cs"
        if not main_file.exists():
            continue
        src_text = _read(main_file)
        m = re.search(r"PRIORITY\s*=\s*(\d+)", src_text)
        if not m:
            continue
        priority = m.group(1)
        # Check that this priority appears in the ADR.
        # The ADR table format is: `| Domain | PRIORITY | <rest>`
        # We do a permissive search: look for the priority value in a line that
        # also mentions the domain name (case-sensitive).
        adr_line_pattern = re.compile(
            rf"\|\s*{re.escape(f)}\s*\|[^|\n]*{priority}[^|\n]*\|",
            re.MULTILINE,
        )
        if not adr_line_pattern.search(adr_text):
            # Fallback: check if any line in the ADR mentions both the domain name and the priority.
            simple_pattern = re.compile(rf"\b{re.escape(f)}\b.*{priority}|{priority}.*\b{re.escape(f)}\b")
            if not simple_pattern.search(adr_text):
                missing_in_adr.append(f"{f} (priority {priority} not in ADR)")
    assert not missing_in_adr, (
        f"Domain(s) with PRIORITY not in ADR-0004: {missing_in_adr}. "
        f"Either update the ADR table or fix the source PRIORITY value."
    )


def test_mod_cs_uses_dotted_namespace_patterns() -> None:
    """Mod.cs should consistently use plain `CivicSurvival.Domains.X;` imports.

    A `using CivicSurvival.Domains.X.Y;` is allowed for sub-namespaces. A bare
    `using CivicSurvival.Domains;` is also valid (used for some Core.Features namespaces).
    """
    text = _read(MOD_CS)
    bad = re.findall(r"using\s+CivicSurvival\.Domains\b(?!\.\w)", text)
    assert not bad, (
        f"Bare `using CivicSurvival.Domains;` imports found in Mod.cs (without "
        f"specific namespace). Prefer specific imports: {bad}."
    )


if __name__ == "__main__":
    import subprocess
    import sys

    rc = subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"])
    sys.exit(rc)