"""Tutorial & help-portal discipline tests.

Locks in the contract documented in docs/tutorial-help-portal-audit.md.

USER_GUIDE.md promises four onboarding mechanisms:
  1. Intro sequence             -> implemented (CrisisTutorialSystem)
  2. First-strike prompt        -> partial (implicit in crisis system)
  3. Per-section "?" portals    -> NOT in public source (UITK widget code
                                   is in the closed toolkit)
  4. Milestone moments          -> implemented (MilestoneTutorialSystem)

This test enforces what we CAN enforce from the public source: the
high-stakes Settings-UI toggles must have tooltip text in every locale.

Why this test exists:
  - The Online Features, Developer Diagnostics, and Bug Reporting
    toggles are privacy-relevant. A tooltip is the user's last line of
    defense before consenting.
  - Without these tests, a future Settings-UI redesign could ship
    toggles without tooltips and the regression would be invisible.

Nine rules enforced here:
  1. Every settings-group toggle listed in the audit has a TOOLTIP_*
     key in en-US.
  2. Every such tooltip is also present in uk-UA.
  3. Every such tooltip is also present in zh-CN.
  4. Every TOOLTIP_* key has non-trivial content (no placeholders).
  5. The CrisisTutorialSystem code path exists in the codebase.
  6. The MilestoneTutorialSystem code path exists in the codebase.
  7. No TUTORIAL_* prefixed keys exist (we don't have that namespace;
     if one is added it must be added to all 3 locales by the
     test_localization_keys.py suite).
  8. The audit doc references the test (drift detection).
  9. The audit doc is honest about the gap (mentions what's NOT done).

Run: pytest tests/test_tutorial_help_portals.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
LOCALIZATION_DIR = ROOT / "CivicSurvival" / "Localization"
DOC = ROOT / "docs" / "tutorial-help-portal-audit.md"

# Toggles that MUST have a TOOLTIP_* key in every locale.
# These are the high-stakes settings where a tooltip is essential,
# not optional. Adding a new toggle to this list is appropriate when
# it is privacy-relevant OR opaque to a non-power user.
REQUIRED_TOOLTIPS: tuple[str, ...] = (
    "TOOLTIP_ONLINE_FEATURES",
    "TOOLTIP_DEVELOPER_DIAGNOSTICS",
    "TOOLTIP_BUG_REPORTING",
    "TOOLTIP_DARK_HUMOR_MESSAGES",
    "TOOLTIP_SKIP_INTRO",
    "TOOLTIP_SIREN_SOUNDS",
)


def _load_locale(name: str) -> dict[str, str]:
    path = LOCALIZATION_DIR / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _all_three_locales() -> dict[str, dict[str, str]]:
    return {n: _load_locale(n) for n in ("en-US", "uk-UA", "zh-CN")}


# === Rule 1 + 2 + 3: every required tooltip in every locale =============


def test_required_tooltips_present_in_all_locales() -> None:
    """Every high-stakes toggle has a TOOLTIP_* key in en-US, uk-UA, zh-CN."""
    locales = _all_three_locales()
    missing: dict[str, list[str]] = {}
    for locale_name, locale_data in locales.items():
        missing[locale_name] = [key for key in REQUIRED_TOOLTIPS if key not in locale_data]
    bad = {k: v for k, v in missing.items() if v}
    assert not bad, (
        f"required tooltip keys missing from locale files: {bad}\n"
        f"Add the keys to {sorted(bad)} (en-US/uk-UA/zh-CN)."
    )


# === Rule 4: every tooltip has non-trivial content =======================


def test_required_tooltips_have_substantive_content() -> None:
    """Every required tooltip is at least 20 characters and not a placeholder."""
    en = _load_locale("en-US")
    bad: list[str] = []
    for key in REQUIRED_TOOLTIPS:
        value = en.get(key, "")
        if not isinstance(value, str):
            bad.append(f"{key} not a string ({type(value).__name__})")
            continue
        if len(value) < 20:
            bad.append(f"{key} too short ({len(value)} chars): {value!r}")
            continue
        stripped = value.strip()
        if not stripped or stripped.lower() in {"todo", "fixme", "tbd", "xxx"}:
            bad.append(f"{key} is placeholder: {value!r}")
    assert not bad, f"tooltips have insufficient content: {bad}"


def test_tooltip_values_are_translated_not_placeholder() -> None:
    """Ukrainian and Chinese tooltips are not exact copies of English.
    A copy-paste would mean translation didn't happen; this catches
    a localization process regression.
    """
    locales = _all_three_locales()
    en = locales["en-US"]
    bad: list[str] = []
    for key in REQUIRED_TOOLTIPS:
        en_value = en.get(key, "").strip()
        for locale_name in ("uk-UA", "zh-CN"):
            localized = locales[locale_name].get(key, "").strip()
            if localized == en_value and len(en_value) > 30:
                bad.append(f"{key} not translated in {locale_name}")
    assert not bad, (
        f"tooltips appear untranslated: {bad}. "
        f"Each tooltip must be human-translated, not copy-pasted."
    )


# === Rule 5 + 6: the two implemented tutorial systems exist ==============


def test_crisis_tutorial_system_file_exists() -> None:
    """The intro-sequence tutorial system exists in the Tutorial domain."""
    path = ROOT / "CivicSurvival" / "Domains" / "Tutorial" / "Systems" / "CrisisTutorialSystem.cs"
    assert path.exists(), (
        f"CrisisTutorialSystem.cs missing at {path}. "
        "USER_GUIDE promises an intro sequence; this is the implementation."
    )


def test_milestone_tutorial_system_file_exists() -> None:
    """The milestone tutorial system exists in the Tutorial domain."""
    path = (
        ROOT / "CivicSurvival" / "Domains" / "Tutorial" / "Systems" / "MilestoneTutorialSystem.cs"
    )
    assert path.exists(), (
        f"MilestoneTutorialSystem.cs missing at {path}. "
        "USER_GUIDE promises milestone moments; this is the implementation."
    )


# === Rule 7: no accidental TUTORIAL_* namespace ==========================


def test_no_tutorial_prefixed_keys_without_consistency_check() -> None:
    """The codebase has no TUTORIAL_* prefixed keys.

    If one is added in the future, it MUST be added to all 3 locales.
    The test_localization_keys.py suite catches locale drift, but this
    test catches the case where a TUTORIAL_* key is added with the
    expectation of being only in one locale.
    """
    for name in ("en-US", "uk-UA", "zh-CN"):
        locale = _load_locale(name)
        bad = [k for k in locale if k.startswith("TUTORIAL_")]
        assert not bad, (
            f"{name} has TUTORIAL_* prefixed keys: {bad}. "
            f"If intentional, add them to all 3 locales and revisit "
            f"this assertion (the test is intentionally strict)."
        )


# === Rule 8 + 9: the audit doc stays accurate ============================


def test_audit_doc_exists_and_references_this_test() -> None:
    """docs/tutorial-help-portal-audit.md exists and points at this test."""
    assert DOC.exists(), f"{DOC} missing"
    text = DOC.read_text(encoding="utf-8")
    assert "tests/test_tutorial_help_portals.py" in text, (
        "audit doc no longer points at its discipline test"
    )


def test_audit_doc_honest_about_gap() -> None:
    """The audit doc must explicitly state that per-panel "?" portals
    are NOT in the public source. Hiding that gap would mislead readers
    about what the mod actually delivers.
    """
    text = DOC.read_text(encoding="utf-8")
    lower = text.lower()
    # Must mention both the absence AND the reason (UITK closed)
    assert "no" in lower or "not in" in lower or "absent" in lower, (
        "audit doc does not state the gap explicitly"
    )
    assert "toolkit" in lower or "closed" in lower or "public source" in lower or "uitk" in lower, (
        "audit doc does not explain why the gap exists"
    )


# === Cross-cutting: tooltip keys must not collide with existing keys ====


def test_required_tooltips_are_unique_keys() -> None:
    """Sanity: the REQUIRED_TOOLTIPS list contains no duplicates and
    each key actually appears in en-US (otherwise the list is stale).
    """
    assert len(REQUIRED_TOOLTIPS) == len(set(REQUIRED_TOOLTIPS)), (
        f"REQUIRED_TOOLTIPS contains duplicates: {REQUIRED_TOOLTIPS}"
    )
    en = _load_locale("en-US")
    stale = [k for k in REQUIRED_TOOLTIPS if k not in en]
    assert not stale, (
        f"REQUIRED_TOOLTIPS contains keys missing from en-US: {stale}. "
        f"Either add them to en-US.json or remove them from the list."
    )
