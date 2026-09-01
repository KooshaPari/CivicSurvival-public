# Accessibility Notes

This document records the **accessibility commitments** for the
CivicSurvival in-game UI and the supporting documentation.

## Scope

The in-game UI is rendered via Unity's UI Toolkit (`UI Toolkit`),
which is screen-reader compatible on PC with the appropriate OS
assistive tech bridge. This document covers:

* UI color contrast (WCAG 2.1 AA as the floor).
* Keyboard-only navigability.
* Screen-reader labels.
* Subtitle / caption rendering for cutscenes.
* Reduced-motion mode for cinematic transitions.
* Localization-as-accessibility (per-locale string widths in CJK
  languages affect layout).

## Concrete commitments

| Item | Where | Target |
|---|---|---|
| Text contrast | `CivicSurvival/UI/Themes/*.css` | WCAG 2.1 AA on all UI states (normal, hover, disabled) |
| Subtitles | `CivicSurvival/Domains/Narrative/Rendering/SubtitleRenderer.cs` | 100% of cutscene audio has subtitle asset |
| Font scale | `CivicSurvival/UI/Settings/TextScaleSlider.cs` | 100% – 200% in 25% increments, layout-adaptive |
| Color-blind mode | `CivicSurvival/UI/Settings/ColorblindMode.cs` | Protanope / Deuteranope / Tritanope palettes available |
| Reduced motion | `CivicSurvival/UI/Settings/ReducedMotionToggle.cs` | Disables non-essential transitions |
| Keyboard focus | `CivicSurvival/UI/Layout/*.uxml` | All interactive elements reachable via Tab; visible focus ring |
| Screen-reader labels | `CivicSurvival/Localization/en-US.json` (then propagated to uk-UA/zh-CN) | Every interactive element has a non-empty `aria-label` |

## Where we are **not** there yet

* **Custom bind remapping for action keys** -- currently uses the
  default Paradox binds; a remap UI is planned for 0.5.x.
* **Voice-control / dwell-click support** -- not planned; the UI is
  pointer + keyboard.
* **High-contrast/full-dark theme** -- partial; see the colorblind
  modes for now.

## Testing

UI accessibility is not tested in the public test suite (it requires
the CS2 runtime); the closed-source QA harness runs automated
contrast + focus-order checks. New UI code that introduces a new
interactive element must declare the aria-label string in a locale
key and add it to the translation queue.

## For modders

If your mod adds a UI element, please:

1. Declare an aria-label key (e.g. `MOD_MY_THING_LABEL`) in
   `CivicSurvival/Localization/en-US.json` (and the other locales).
2. Use the existing theme tokens (`color_text_primary`, etc.)
   instead of hardcoded hex values.
3. Test keyboard reachability before publishing the mod.

---

Last updated: 2026-09-01.
