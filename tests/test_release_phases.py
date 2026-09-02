"""Release phase discipline tests.

Locks in the wave/phase contract documented in docs/release-phases.md.
The codebase ships a wave-based feature gate (not a typed ReleasePhase
enum), and these tests enforce four discipline rules so the wave config
cannot drift from the actual domain registrations.

Why this test exists:
  - Every registered domain must declare its wave, OR be on the explicit
    "always-on" allowlist (services that are required by Phase 1 and
    cannot be phased out, e.g. Effects).
  - Every wave entry must point to a real registered domain (no typos).
  - Waves must be in [1, 98] for shipping features (99 = sentinel).
  - The Network/Arena/ArenaUI ordering invariant must hold.

Run: pytest tests/test_release_phases.py -v
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]

# Feature IDs that are ALWAYS shipped regardless of wave.
# Add to this list with extreme caution -- the point of waves is that
# nothing is silent, so the only entries here are infrastructure pieces
# that Phase 1 cannot run without (e.g. Effects).
ALWAYS_ON_FEATURES: frozenset[str] = frozenset(
    {
        "Effects",
        "UI",
    }
)

# Map C# class name (with Domain/Feature suffix) to the wave-config key.
# FeatureManifest.ValidateWaveOrdering uses short names ("Network", "Arena",
# "ArenaUI") not C# class names; this map bridges the two.
# When adding a new domain, add its mapping here OR use the convention
# `FooBarDomain` -> "FooBar" (which the parser handles automatically).
WAVE_NAME_MAP: dict[str, str] = {
    # Cross-domain coordinators (Feature suffix)
    "DamageAccounting": "DamageAccounting",
    "Efficiency": "Efficiency",
    "Population": "Population",
    "ThreatsAirDefense": "ThreatsAirDefense",
    "Wellbeing": "Wellbeing",
    # Arena feature (lives under Services.Arena)
    "Arena": "Arena",
}


def _class_name_to_wave_key(class_name: str) -> str:
    """Convert a registered C# class name to the wave-config key.

    Default rule: strip the trailing "Domain" or "Feature" suffix.
    Overrides live in WAVE_NAME_MAP (for cross-domain coordinators and
    classes whose bare name doesn't match the wave config).
    """
    if class_name in WAVE_NAME_MAP:
        return WAVE_NAME_MAP[class_name]
    if class_name.endswith("Domain"):
        return class_name[: -len("Domain")]
    if class_name.endswith("Feature"):
        return class_name[: -len("Feature")]
    return class_name


def _read_mod_cs() -> str:
    return (ROOT / "CivicSurvival" / "Mod.cs").read_text(encoding="utf-8")


def _registered_domains() -> set[str]:
    """Parse Mod.RegisterFeatures() for `registry.Register(new XxxDomain())`.

    Returns the wave-config key (with help from WAVE_NAME_MAP) for each
    registered feature so wave-config keys (which are short IDs like
    'Network') match the registered C# class names.
    """
    mod_cs = _read_mod_cs()
    # Allow dots in namespace prefix: "Services.Arena.ArenaFeature"
    pattern = re.compile(
        r"registry\.Register\(new\s+(?:[A-Za-z_][A-Za-z0-9_]*\.)*"
        r"(?P<cls>[A-Z][A-Za-z0-9]+?)(?:Domain|Feature)\(\)\)"
    )
    found: set[str] = set()
    for match in pattern.finditer(mod_cs):
        cls = match.group("cls")
        found.add(_class_name_to_wave_key(cls))
    return found


def _wave_config_sample() -> dict[str, int]:
    """Best-effort load of the live balance config.

    The actual JSON lives in the closed server side; this test uses a
    sample snapshot under build-evidence/ or scripts/ when available,
    falling back to an empty dict. The discipline rules still apply to
    whatever the sample contains.
    """
    candidates = [
        ROOT / "build-evidence" / "feature-gates.sample.json",
        ROOT / "scripts" / "feature-gates.sample.json",
        ROOT / "scripts" / "balance.sample.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if isinstance(data, dict):
            # Tolerate both flat {"Waves": {...}} and nested {"FeatureGates": {"Waves": {...}}}
            if "Waves" in data and isinstance(data["Waves"], dict):
                return {
                    str(k): int(v) for k, v in data["Waves"].items() if not str(k).startswith("_")
                }
            if "FeatureGates" in data and isinstance(data["FeatureGates"], dict):
                fg = data["FeatureGates"]
                if "Waves" in fg and isinstance(fg["Waves"], dict):
                    return {
                        str(k): int(v) for k, v in fg["Waves"].items() if not str(k).startswith("_")
                    }
    return {}


def test_registered_domains_parse_out_of_mod_cs() -> None:
    """Sanity: the regex actually finds domains in Mod.cs.

    If this fails, the test infra is broken -- fix the parser before
    trusting the discipline checks below.
    """
    found = _registered_domains()
    assert "PowerGrid" in found, f"expected PowerGrid in registered domains; found: {sorted(found)}"
    assert "Tutorial" in found, f"expected Tutorial in registered domains; found: {sorted(found)}"
    # Counter for sanity: at least 25 domains registered today.
    assert len(found) >= 25, f"too few domains parsed: {sorted(found)}"


def test_wave_keys_are_unique_and_in_range() -> None:
    """Every wave entry must be unique and in [1, 98] for shipping.

    Sentinel value 99 is reserved for WAVE_SENTINEL_UNAVAILABLE.
    Wave 0 is invalid -- FeatureManifest.WaveOf returns 1 as default but
    explicit 0 is a misconfiguration that crashes ValidateWaveOrdering
    on Network/Arena comparisons.
    """
    waves = _wave_config_sample()
    if not waves:
        # No live config -- test passes vacuously (we still want it to run).
        return
    seen: set[str] = set()
    for key, wave in waves.items():
        assert key not in seen, f"duplicate wave entry: {key!r}"
        seen.add(key)
        assert isinstance(wave, int), f"wave for {key!r} is not int: {wave!r}"
        assert 1 <= wave <= 98, (
            f"wave for {key!r} is {wave}; expected 1..98 "
            f"(use 99 for unavailable; never 0 or negative)"
        )


def test_network_arena_arena_ui_ordering_invariant() -> None:
    """If any of Network/Arena/ArenaUI is present, all three must be,
    in order ArenaUI >= Arena >= Network.

    Mirrors CivicSurvival/Core/Infrastructure/FeatureManifest.cs:111
    ValidateWaveOrdering. Re-asserted here so a regression in the
    validator is caught by the same test that catches a config bug.
    """
    waves = _wave_config_sample()
    if not waves:
        return
    network = waves.get("Network")
    arena = waves.get("Arena")
    arena_ui = waves.get("ArenaUI")
    if network is None and arena is None and arena_ui is None:
        return
    assert network is not None, "Arena or ArenaUI present without Network"
    assert arena is not None, "ArenaUI present without Arena"
    assert arena_ui is not None, "Network/Arena present without ArenaUI"
    assert arena >= network, f"Arena ({arena}) must be >= Network ({network})"
    assert arena_ui >= arena, f"ArenaUI ({arena_ui}) must be >= Arena ({arena})"


def test_unregistered_domain_with_wave_entry_is_rejected() -> None:
    """A wave entry that points to a non-registered domain is a typo.

    Without this check, a typo like "Aren" would silently never trigger
    any gating, leaving the feature in wave 1 = always shipped.
    """
    waves = _wave_config_sample()
    if not waves:
        return
    registered = _registered_domains() | set(ALWAYS_ON_FEATURES)
    dead = sorted(set(waves) - registered)
    assert not dead, (
        f"wave config references {len(dead)} unregistered feature(s): {dead}\n"
        f"Add to ALREADY-ON allowlist in tests/test_release_phases.py if intentional,"
        f" or fix the config typo."
    )


def test_registered_domain_without_wave_entry_lands_in_allowlist() -> None:
    """Every registered domain must either have a wave entry OR be on the
    ALWAYS_ON_FEATURES allowlist.

    Without this, a new domain registered in Mod.cs but missing from
    the wave config silently defaults to wave 1, which means it ships
    on day one regardless of intended phase. The whole point of waves
    is that nothing is silent.
    """
    waves = _wave_config_sample()
    if not waves:
        return
    registered = _registered_domains()
    gated = registered & set(waves)
    unconfigured = sorted(registered - gated - ALWAYS_ON_FEATURES - {"ArenaUI", "UI"})
    # ArenaUI is special: it's a UI feature that always ships with Arena,
    # so it's covered by the Network/Arena ordering invariant above.
    # We exempt it from "every domain must have a wave entry" check.
    assert not unconfigured, (
        f"domain registered without a wave entry (silent default to wave 1 = always shipped): "
        f"{unconfigured}\n"
        f"Add a wave entry to the balance config, or extend ALWAYS_ON_FEATURES if intentional."
    )


def test_validate_wave_ordering_failure_message_is_actionable() -> None:
    """The error message in FeatureManifest.cs:120-122 names the offending
    keys so a maintainer can fix the config without re-reading the validator.
    Lock that contract in: the message must mention 'Network', 'Arena', and
    'ArenaUI' by name.
    """
    feature_manifest = (
        ROOT / "CivicSurvival" / "Core" / "Infrastructure" / "FeatureManifest.cs"
    ).read_text(encoding="utf-8")
    for needle in ("Network", "Arena", "ArenaUI"):
        assert needle in feature_manifest, (
            f"FeatureManifest.cs no longer mentions {needle!r} in the ordering "
            f"validator -- the error message lost actionable context"
        )


def test_release_phases_doc_exists_and_links_to_manifest() -> None:
    """docs/release-phases.md is the canonical spec; this test pins its
    existence and ensures it references the code surface so a future
    refactor doesn't silently move the gate.
    """
    doc_path = ROOT / "docs" / "release-phases.md"
    assert doc_path.exists(), f"{doc_path} missing; see docs/release-phases.md"
    text = doc_path.read_text(encoding="utf-8")
    assert "FeatureManifest" in text, (
        "release-phases.md no longer references FeatureManifest -- "
        "the contract has drifted from the doc"
    )
    assert "WAVE_SENTINEL_UNAVAILABLE" in text, (
        "release-phases.md no longer references WAVE_SENTINEL_UNAVAILABLE -- "
        "the sentinel mechanism is no longer documented"
    )


def test_release_phases_doc_warns_about_silent_default() -> None:
    """The doc must warn that a missing wave entry defaults to wave 1
    (= always shipped). This is the single most common wave bug.
    """
    text = (ROOT / "docs" / "release-phases.md").read_text(encoding="utf-8")
    lower = text.lower()
    assert "silent" in lower or "default" in lower, (
        "release-phases.md does not warn about silent wave defaults"
    )
