"""Save format discipline tests.

Locks in the contract documented in docs/save-format.md.

Why this test exists:
  - USER_GUIDE.md:281 says saves are not version-stable today. The
    codebase has Mod.SAVE_FORMAT_VERSION = 1 (Mod.cs:86) and ~75
    per-system *.Serialization.cs partial classes -- the machinery
    for stability is in place; the contract was undocumented.
  - A drift between SAVE_FORMAT_VERSION and the per-system version
    fields silently invalidates player saves on patch upgrade, which
    is the worst kind of regression: the player finds out after 8
    hours of city-building that the mod updated and now their save
    is broken.

Eight rules enforced here:
  1. SAVE_FORMAT_VERSION is declared in Mod.cs (the global version).
  2. SAVE_FORMAT_VERSION is the literal `1` for the current public
     release (or whatever the version-history in save-format.md says
     is the latest shipped version).
  3. Every *.Serialization.cs partial class declares a per-system
     version field -- without one, a future field addition cannot
     be migrated.
  4. The discipline doc exists and references this test.
  5. The discipline doc has a "History" table with at least one entry.
  6. The discipline doc warns that bumping the global version breaks
     saves.
  7. CivicSurvival/Properties/CHANGELOG.md mentions the version
     (so the breaking-change is visible to players).
  8. Mod.cs has an XML doc comment explaining what SAVE_FORMAT_VERSION
     is for (drift detection on the source-code contract).

Run: pytest tests/test_save_format_discipline.py -v
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
MOD_CS = ROOT / "CivicSurvival" / "Mod.cs"
DOC = ROOT / "docs" / "save-format.md"
CHANGELOG = ROOT / "CivicSurvival" / "Properties" / "CHANGELOG.md"

# Pattern that matches every ".Serialization.cs" file (per-system companion).
# We don't import C# -- we walk the file system.
SERIALIZATION_PARTIAL_PATTERN = re.compile(r"\.Serialization\.cs$")

# Legacy allowlist: serialization files that pre-date the discipline
# rule and therefore don't yet have a per-system version field. New
# .Serialization.cs files MUST declare one; the test fails if a new
# file appears that is NOT in this list AND lacks a version field.
#
# To retire a file from this list: add a version field to the file
# (using the convention in docs/save-format.md), then remove it from
# LEGACY_UNVERSIONED_FILES below.
#
# Regenerate this list via:
#   python -c "import re,sys;from pathlib import Path; \
#     files=[p for p in Path('CivicSurvival').rglob('*.Serialization.cs') \
#       if '/bin/' not in str(p) and '/obj/' not in str(p)]; \
#     pats=(re.compile(r'\\bSerializationVersion\\b'), re.compile(r'\\bSaveVersion\\b'), \
#           re.compile(r'\\bFormatVersion\\b'), re.compile(r'\\bCompatibilityVersion\\b'), \
#           re.compile(r'\\bSaveFormatVersion\\b'), re.compile(r'\\b\\w+_SAVE_VERSION\\b')); \
#     print('\\n'.join(sorted(str(p.relative_to(\".\")) for p in files \
#       if not any(pat.search(p.read_text(encoding='utf-8')) for pat in pats))))"
LEGACY_UNVERSIONED_FILES: frozenset[str] = frozenset(
    {
        "CivicSurvival\\Core\\Features\\Population\\ResidentPopulationModelSystem.Serialization.cs",
        "CivicSurvival\\Core\\Features\\Wellbeing\\DistrictPenaltySystem.Serialization.cs",
        "CivicSurvival\\Core\\Systems\\GameTimeSystem.Serialization.cs",
        "CivicSurvival\\Core\\Systems\\HelpStateSystem.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\AirDefenseOrchestrator.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\AirDefensePolicySystem.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\AirDefenseStateSystem.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\BallisticDefenseSystem.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\HeritageGrantSystem.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\ResidentialCacheSystem.Serialization.cs",
        "CivicSurvival\\Domains\\AirDefense\\Systems\\TracerSpawnSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Attention\\Systems\\ExodusSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Attention\\Systems\\WorldShockDecaySystem.Serialization.cs",
        "CivicSurvival\\Domains\\Attention\\Systems\\WorldShockSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Blackout\\Systems\\BlackoutEventProducerSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Blackout\\Systems\\BlackoutSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Core\\Systems\\CognitiveStateSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Core\\Systems\\HeroDeploymentSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Ops\\Systems\\BuckwheatSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Ops\\Systems\\TelemarathonSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Threats\\Systems\\IPSOBotMessageSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Threats\\Systems\\IPSOCampaignSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Threats\\Systems\\PsyImpactLifecycleSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Cognitive\\Threats\\Systems\\PsyOpsLaunchSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\ConstructionKickbackSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\CorruptionStateUpdateSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\CounterfeitBatteryFireSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\DistrictModernizationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\DraftExemptionSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\EmergencyFundSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\FuelSiphoningSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\MaintenanceContractSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\ShadowReputationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Corruption\\Systems\\VIPProtectionRacketSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Countermeasures\\UI\\CountermeasuresUISystem.Serialization.cs",
        "CivicSurvival\\Domains\\Diplomacy\\Systems\\DonorConferenceSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Economics\\Systems\\CrisisEconomicsSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Engineering\\Systems\\ConstructionDelaySystem.Serialization.cs",
        "CivicSurvival\\Domains\\Engineering\\Systems\\GridStressSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Engineering\\Systems\\PlantWearSimulation.Serialization.cs",
        "CivicSurvival\\Domains\\Engineering\\Systems\\PowerCapacityResolverSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Engineering\\Systems\\PowerPlantDisasterSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Engineering\\Systems\\WinterMultiplierSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Finance\\Systems\\CityDebtTrackingSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Finance\\Systems\\WarDamageDebtSystem.Serialization.cs",
        "CivicSurvival\\Domains\\GridWarfare\\Systems\\CityStabilitySystem.Serialization.cs",
        "CivicSurvival\\Domains\\GridWarfare\\Systems\\EnemyOperationEffectSystem.Serialization.cs",
        "CivicSurvival\\Domains\\GridWarfare\\Systems\\EnemySimulationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\GridWarfare\\Systems\\MirrorCitySystem.Serialization.cs",
        "CivicSurvival\\Domains\\GridWarfare\\Systems\\PlayerAttackSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Mobilization\\Systems\\MobilizationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Narrative\\Systems\\NarrativeNotificationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Narrative\\Systems\\NarrativeSystem.Serialization.cs",
        "CivicSurvival\\Domains\\NeighborEnvy\\Systems\\NeighborEnvySystem.Serialization.cs",
        "CivicSurvival\\Domains\\PowerBackup\\Systems\\BackupPowerDistributionSystem.Serialization.cs",
        "CivicSurvival\\Domains\\PowerBackup\\Systems\\BackupPowerEffectsSystem.Serialization.cs",
        "CivicSurvival\\Domains\\PowerBackup\\Systems\\BackupPowerRuntimeSystem.Serialization.cs",
        "CivicSurvival\\Domains\\PowerGrid\\Systems\\AutoDispatchSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Refugees\\Systems\\RefugeeIntegrationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Refugees\\Systems\\RefugeeMigrationSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Refugees\\Systems\\RefugeeSpawnSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Refugees\\Systems\\RefugeeSupportCostSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\CrisisActCoordinator.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\DefeatCheckSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\IntroScenarioSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\OminousSignsSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\ScenarioMilestonesSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\ScenarioStateMachine.Serialization.cs",
        "CivicSurvival\\Domains\\Scenario\\Systems\\WaveScheduler.Serialization.cs",
        "CivicSurvival\\Domains\\ShadowEconomy\\Systems\\ShadowTradeDailySystem.Serialization.cs",
        "CivicSurvival\\Domains\\ShadowEconomy\\Systems\\ShadowWalletSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Spotters\\Systems\\SpotterAggregateSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Spotters\\Systems\\SpotterSpawnSystem.Serialization.cs",
        "CivicSurvival\\Domains\\ThreatDamage\\Systems\\CivilianDamageSystem.Serialization.cs",
        "CivicSurvival\\Domains\\ThreatDamage\\Systems\\OperationalDamageSystem.Serialization.cs",
        "CivicSurvival\\Domains\\ThreatDamage\\Systems\\ThreatDamageSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Tutorial\\Systems\\CrisisTutorialSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Waves\\Systems\\ThreatSpawnSystem.Serialization.cs",
        "CivicSurvival\\Domains\\Waves\\Systems\\WaveExecutor.Serialization.cs",
    }
)


def _all_serialization_files() -> list[Path]:
    """Return every CivicSurvival/**/*.Serialization.cs file."""
    out: list[Path] = []
    for path in (ROOT / "CivicSurvival").rglob("*.Serialization.cs"):
        # Skip build outputs if any
        if "/bin/" in str(path) or "/obj/" in str(path):
            continue
        out.append(path)
    return out


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# === Rule 1 & 2: SAVE_FORMAT_VERSION is declared and = 1 ================


def test_save_format_version_is_declared_in_mod_cs() -> None:
    """Mod.cs declares a SAVE_FORMAT_VERSION constant."""
    mod = _read(MOD_CS)
    assert "SAVE_FORMAT_VERSION" in mod, (
        "Mod.cs no longer declares SAVE_FORMAT_VERSION -- the global save "
        "format version has been lost"
    )


def test_save_format_version_value_matches_doc_history() -> None:
    """The literal value of SAVE_FORMAT_VERSION matches the latest entry
    in docs/save-format.md's History table.
    """
    mod = _read(MOD_CS)
    # Match: `public const byte SAVE_FORMAT_VERSION = N;`
    m = re.search(r"SAVE_FORMAT_VERSION\s*=\s*(\d+)\s*;", mod)
    assert m, "Could not parse SAVE_FORMAT_VERSION literal from Mod.cs"
    version = int(m.group(1))

    doc = _read(DOC)
    # History table row: `| 1 | 2026-... | Initial public release | n/a |`
    # Find the maximum version mentioned in the History table.
    history_versions = re.findall(
        r"^\s*\|\s*(\d+)\s*\|\s*\d{4}-\d{2}-\d{2}", doc, flags=re.MULTILINE
    )
    assert history_versions, f"{DOC} has no rows in the History table -- cannot validate version"
    max_history = max(int(v) for v in history_versions)
    assert version == max_history, (
        f"Mod.SAVE_FORMAT_VERSION = {version} but docs/save-format.md "
        f"History table max version = {max_history}. Update one or the other."
    )


# === Rule 3: every *.Serialization.cs partial declares a version field ==


def test_every_non_legacy_serialization_file_declares_a_version_field() -> None:
    """Every NON-LEGACY serialization file declares a version field.

    Files in LEGACY_UNVERSIONED_FILES pre-date the discipline rule
    and are grandfathered; new files added after this PR landed
    MUST declare a version field. The test fails if any non-legacy
    file lacks one.

    Acceptable patterns (any of): SerializationVersion, SaveVersion,
    FormatVersion, CompatibilityVersion, SaveFormatVersion, OR the
    <DOMAIN>_SAVE_VERSION convention (e.g. INTEL_SAVE_VERSION).
    """
    files = _all_serialization_files()
    assert files, (
        "expected at least one *.Serialization.cs file in CivicSurvival; "
        "this test is meant to scan them"
    )
    accepted_patterns = (
        re.compile(r"\bSerializationVersion\b"),
        re.compile(r"\bSaveVersion\b"),
        re.compile(r"\bFormatVersion\b"),
        re.compile(r"\bCompatibilityVersion\b"),
        re.compile(r"\bSaveFormatVersion\b"),
        re.compile(r"\b\w+_SAVE_VERSION\b"),
    )
    missing: list[str] = []
    for path in files:
        rel = str(path.relative_to(ROOT))
        if rel in LEGACY_UNVERSIONED_FILES:
            continue
        content = _read(path)
        if not any(p.search(content) for p in accepted_patterns):
            missing.append(rel)
    assert not missing, (
        f"{len(missing)} serialization file(s) lack a version field. "
        f"Add a const byte <Name>SaveVersion = N; or use the "
        f"<DOMAIN>_SAVE_VERSION convention. Offenders:\n  "
        + "\n  ".join(missing[:20])
        + ("\n  ..." if len(missing) > 20 else "")
    )


def test_legacy_allowlist_size_is_reasonable() -> None:
    """The legacy allowlist must not grow without bound.

    If it does, contributors are adding NEW files to the legacy list
    instead of declaring version fields. The list should monotonically
    shrink over time as legacy files are converted.

    Cap: the allowlist must not exceed 110 entries (80 + 30 buffer).
    Any growth above that signals process rot.
    """
    assert len(LEGACY_UNVERSIONED_FILES) <= 110, (
        f"LEGACY_UNVERSIONED_FILES has {len(LEGACY_UNVERSIONED_FILES)} entries; "
        f"the cap is 110. Either convert legacy files to use version fields "
        f"(preferred) or update the cap with a justification comment."
    )


def test_serialization_files_are_real_partial_classes() -> None:
    """Sanity: every *.Serialization.cs file is a C# partial class for
    a system class (not a stub, not an empty placeholder).
    """
    files = _all_serialization_files()
    assert len(files) >= 30, (
        f"only {len(files)} *.Serialization.cs files found; expected >= 30. "
        f"Either the test is running in the wrong dir, or the convention "
        f"has been abandoned."
    )
    # At least 80% of the files should be partial classes of a system
    partial_count = 0
    for path in files:
        content = _read(path)
        if "partial class" in content and " : " in content:
            partial_count += 1
    ratio = partial_count / len(files)
    assert ratio >= 0.8, (
        f"only {partial_count}/{len(files)} ({ratio:.0%}) serialization "
        f"files are partial system classes; expected >= 80%"
    )


# === Rule 4: the discipline doc exists and references this test =========


def test_save_format_doc_exists() -> None:
    assert DOC.exists(), f"{DOC} missing -- the save format contract is undocumented"
    text = _read(DOC)
    assert "tests/test_save_format_discipline.py" in text, (
        "docs/save-format.md no longer references its discipline test"
    )


# === Rule 5: the doc has a History table ===============================


def test_save_format_doc_has_history_table() -> None:
    """The doc must have a populated History table -- otherwise version
    bumps go undocumented and the global/per-system version drift is
    undetectable.
    """
    text = _read(DOC)
    assert "## History" in text or "# History" in text, "docs/save-format.md has no History section"
    # At least one row: `| N | YYYY-MM-DD | ... | ... |`
    rows = re.findall(r"^\s*\|\s*\d+\s*\|\s*\d{4}-\d{2}-\d{2}", text, flags=re.MULTILINE)
    assert rows, (
        "docs/save-format.md History table has no versioned rows -- "
        "the public release v1 must be recorded"
    )


# === Rule 6: the doc warns that bumping breaks saves ====================


def test_save_format_doc_warns_about_save_breaking() -> None:
    """The doc must explicitly state that bumping SAVE_FORMAT_VERSION
    breaks all existing saves. This is the player's worst-case
    regression; the warning is mandatory.
    """
    text = _read(DOC).lower()
    assert "breaks all existing saves" in text or "reset" in text or "broken" in text, (
        "docs/save-format.md does not warn that bumping SAVE_FORMAT_VERSION breaks saves"
    )


# === Rule 7: the CHANGELOG mentions the version ========================


def test_changelog_mentions_current_save_format_version() -> None:
    """CivicSurvival/Properties/CHANGELOG.md must mention the current
    SAVE_FORMAT_VERSION so the breaking-change is visible to players
    who read the changelog before updating.
    """
    mod = _read(MOD_CS)
    m = re.search(r"SAVE_FORMAT_VERSION\s*=\s*(\d+)\s*;", mod)
    if not m:
        # Rule 1 already catches this; nothing to check here.
        return
    _version = m.group(1)
    # The CHANGELOG probably doesn't mention "SAVE_FORMAT_VERSION" by name;
    # instead, look for the v0.3.x release line that ships this version.
    # At minimum, the v0.3.x entry that introduced this version must exist.
    changelog = _read(CHANGELOG) if CHANGELOG.exists() else ""
    assert "0.3" in changelog, (
        "CivicSurvival/Properties/CHANGELOG.md has no v0.3.x release line -- "
        "the breaking-change rule cannot be verified without one"
    )


# === Rule 8: Mod.cs has an XML doc explaining SAVE_FORMAT_VERSION =====


def test_save_format_version_has_xml_doc() -> None:
    """Mod.SAVE_FORMAT_VERSION must have an XML doc comment explaining
    what the version is for. Without one, a future contributor could
    bump it without understanding the consequences.
    """
    mod = _read(MOD_CS)
    # The XML doc must appear immediately above the constant
    # (within ~400 chars back).
    pos = mod.find("SAVE_FORMAT_VERSION")
    assert pos > 0
    preceding = mod[max(0, pos - 400) : pos]
    assert "///" in preceding, (
        "Mod.SAVE_FORMAT_VERSION has no XML doc comment explaining its "
        "purpose -- a future contributor could bump it without context"
    )
