# Feature Flags

CivicSurvival ships 28 game domains (`Domains/`) under one umbrella
project. Each domain is independently toggleable in the in-game
configuration menu, which functions as our **feature-flag system**.

## Why feature flags

* **Modder isolation** -- enable only the domains your mod touches.
* **Compatibility** -- disable domains that conflict with third-party
  mods (e.g. legacy AI controllers vs new `Economics`).
* **Performance profiling** -- disable unused domains to reduce the
  per-tick update cost.
* **Alpha/beta gating** -- new domains ship disabled by default
  and require explicit opt-in via the config menu.

## Where the flags live

* The in-game menu reads from `CivicSurvival/config/config.json`
  (or the player's save state).
* The build-time defaults live in
  `CivicSurvival/Properties/PublishConfiguration.xml` under
  `<EnabledDomains>`.
* The read-side enforcement is in
  `CivicSurvival/Domains/*/Domain.cs` -- each domain gates its
  `Tick()`, `OnEvent()`, and `OnSave()` methods on a single boolean.

## Adding a new flag

1. Add the boolean to `EnabledDomains` in the publish config.
2. Default to `false` for new domains; ship in alpha behind the flag.
3. Document the flag in `CivicSurvival/Properties/CHANGELOG.md`
   under the same release section.
4. Once stable, flip the default to `true` in a subsequent release.
5. Never remove a flag without two release cycles of "deprecated" status
   -- third-party mods depend on them.

## Per-domain flag (example)

```json
// CivicSurvival/config/config.json
{
  "enabled_domains": {
    "AirDefense":     true,
    "Economics":      true,
    "Narrative":      false,   // alpha
    "ThreatFlight":   true,
    "Waves":          true,
    "Telemetry":      true
  }
}
```

## What is *not* a feature flag

* **Performance tuning constants** live in
  `CivicSurvival/Core/Configuration/TuningConstants.cs` -- not flags.
* **Localization** -- per-locale strings are not flags; they are
  always enabled (the active locale chooses at runtime).
* **Build-time `#if` switches** -- the C# build has two:
  `EnableCivicBurst` (off in this public mirror; see csproj) and
  `EnableDiagnostics` (on). These are not flags.

---

Last updated: 2026-09-01.
