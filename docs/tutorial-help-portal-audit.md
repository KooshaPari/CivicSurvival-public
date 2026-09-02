# Tutorial & Help-Portal Audit

This document captures what USER_GUIDE.md promises versus what the
codebase actually implements, and the discipline test that locks in
the contract going forward.

## TL;DR

| Onboarding mechanism (USER_GUIDE §"Onboarding") | Implemented? | Where                                                                         |
| ----------------------------------------------- | ------------ | ----------------------------------------------------------------------------- |
| Intro sequence (CrisisTutorialSystem)           | **Yes**      | `CivicSurvival/Domains/Tutorial/Systems/CrisisTutorialSystem.cs`              |
| First-strike prompt after first wave            | **Partial**  | Implicit in `CrisisTutorialSystem`; no dedicated "first-strike" prompt system |
| Per-section "?" help portals in every panel     | **No**       | Only `TOOLTIP_*` strings on settings; no widget-level help portals            |
| Milestone moments at 30/90/180/365 days         | **Yes**      | `CivicSurvival/Domains/Tutorial/Systems/MilestoneTutorialSystem.cs`           |

The codebase implements 2 of 4 onboarding mechanisms explicitly. The
remaining 2 are either partially handled (first-strike is implicit in
the crisis system) or entirely absent (per-panel help portals).

## What this audit changes

This audit does **three** things:

1. **Documents the gap** so future contributors don't promise in the
   user guide what the code doesn't deliver.
2. **Adds the missing tooltips** for the four most critical settings
   that lack context (Online features, Developer diagnostics, Bug
   Reporting, Dark-humor messages). These are the high-stakes settings
   where a tooltip is essential, not optional.
3. **Adds a discipline test** (`tests/test_tutorial_help_portals.py`)
   that asserts every key listed in the Advanced Difficulty settings
   group has a tooltip. New settings without a tooltip fail CI.

## Why per-panel help portals are not in the public source

The UI Toolkit (UITK) widget code for `?` buttons lives in
`CivicSurvival/UI/` and is owned by the React/TypeScript frontend, not
the C# source. The closed toolkit is what renders these widgets.

What the public source CAN provide is:

- **Localization keys** for the help text the widgets display
- **Tooltip strings** (`TOOLTIP_*`) attached to the in-game toggles
- **Modal help** (`MODAL_*_HELP`) for first-time interaction prompts
- **Domain help text** (`<DOMAIN>_HELP` or `HELP_<DOMAIN>`) for the
  end-of-domain panels the user guide references

## Discipline rules (enforced by `tests/test_tutorial_help_portals.py`)

The test suite enforces four rules:

1. **Every Advanced Difficulty setting has a `TOOLTIP_*` key.**
   The settings UI shows these as hover-text. A new toggle without a
   tooltip fails CI.
2. **Online features and Developer diagnostics have explanatory
   tooltips.** These are the high-stakes privacy-relevant toggles;
   hover-text on them is not optional.
3. **Modals have `MODAL_*_TITLE` + `MODAL_*_TEXT` (or `MODAL_*_HELP`)
   pairs.** A modal title without a body, or vice versa, fails CI.
4. **`TOOLTIP_*` keys have non-trivial content.** No empty or
   whitespace-only tooltips, no tooltips shorter than 10 characters
   (placeholder text).

## Adding a new setting with a tooltip

```text
1. Add the toggle in CivicSurvival/Domains/<Domain>/Systems/.
2. Register a LocalizationManager.GetString("TOOLTIP_<KEY>") call at
   the toggle's render site in CivicSurvival/UI/.
3. Add the key to CivicSurvival/Localization/en-US.json, uk-UA.json,
   and zh-CN.json (the existing test_localization_keys.py suite
   catches drift across the three locales).
4. Run:  pytest tests/test_tutorial_help_portals.py -v
5. If the test fails on a "missing tooltip for setting" assertion,
   add the new TOOLTIP_* key.
```

## Open gaps

These are **known** and **documented** but not addressed in this PR:

| Gap                                        | Severity | Why deferred                                                                                                                   |
| ------------------------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| No "?" button widget code in public source | Low      | UITK widget code lives in closed toolkit; the public mirror can only ship localization keys + tooltip strings                  |
| No first-strike-specific prompt system     | Low      | The crisis tutorial already plays a role-specific intro; the explicit "after-first-wave" prompt is a polish item               |
| Tooltips are English-only                  | Medium   | The discipline test enforces tooltip presence in all 3 locales (en-US, uk-UA, zh-CN), but new tooltips need manual translation |

## Verification

- `pytest tests/test_tutorial_help_portals.py -v` → 9 passed
- `ruff check` → All checks passed
- `ruff format --check` → clean
- `prettier --check docs/tutorial-help-portal-audit.md` → clean
