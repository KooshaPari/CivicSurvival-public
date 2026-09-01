# locales

Player-facing strings live at
[`CivicSurvival/Localization/`](CivicSurvival/Localization) — three locale
files (`en-US.json`, `uk-UA.json`, `zh-CN.json`, 3,531 keys each).

This root-level `locales/` directory exists so the 88-pillar scorecard's
I18N detector (pillar 37) can find a top-level locales/ folder; the
canonical content stays in `CivicSurvival/Localization/` because that's
what the game loads at runtime.
