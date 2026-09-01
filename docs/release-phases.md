# Release Phase System

This document is the **canonical specification** of Civic Survival's release
phasing model. It exists because `USER_GUIDE.md:294-302` mentions four
shipping phases, but the actual gating machinery lives in code without a
documented contract. This file fixes that gap.

## TL;DR

| Phrase in docs/code                | Phrase in this doc             | Where it lives                                                            |
| ---------------------------------- | ------------------------------ | ------------------------------------------------------------------------- |
| "Phase 1 / 2 / 3 / 4" (USER_GUIDE) | **Wave 1 / 2 / 3 / 4**         | `RemoteBalanceConfig.FeatureGates.Waves`                                  |
| "Unavailable / closed"             | **Wave 99 (sentinel)**         | `CivicSurvival.Core.Types.FeatureWaveConstants.WAVE_SENTINEL_UNAVAILABLE` |
| "Preview / dimmed in UI"           | **Future wave below sentinel** | `FeatureManifest.IsPreview()`                                             |
| "Dormant / not registered"         | **Future wave**                | `FeatureManifest.IsWaveReached()` is `false`                              |

## The wave system at a glance

The codebase ships with a **wave-based feature gate** rather than a
named `ReleasePhase` enum. This is deliberate:

- **Waves are numbers, not names.** Adding a "Phase 2.5" requires a code
  change today; with waves, the balance config adds an entry without a
  release. Game studios call this pattern "feature flags as data" — the
  shipping contract is the JSON, not the type system.

- **Three states, one number.** A feature is in exactly one of three
  states at runtime:
  - `wave ≤ currentWave` → **reached** — systems register, UI is live
  - `sentinel > wave > currentWave` → **preview** — UI may dim-render
    from defaults; systems do not register
  - `wave ≥ sentinel (99)` → **unavailable** — permanently closed;
    sentinel value keeps it closed even if `currentWave` reaches 99

- **Single source of truth.** `FeatureManifest.FromBalance(remoteConfig)`
  is built once at `Mod.OnLoad`, captured by `SystemRegistrar.RegisterAll`,
  and frozen for the lifetime of the world. Background refreshes update
  the cache for the next launch but never mutate the active manifest.

## Code surface

| Concept                            | Where                                                                                    |
| ---------------------------------- | ---------------------------------------------------------------------------------------- |
| Sentinel for unavailable features  | `CivicSurvival/Core/Types/FeatureWaveConstants.cs:5` (`WAVE_SENTINEL_UNAVAILABLE = 99`)  |
| Wave-to-state resolution           | `CivicSurvival/Core/Infrastructure/FeatureManifest.cs:44` (`WaveOf`)                     |
| Reached vs preview vs unavailable  | `CivicSurvival/Core/Infrastructure/FeatureManifest.cs:58` (`IsWaveReached`, `IsPreview`) |
| Build manifest from balance config | `CivicSurvival/Core/Infrastructure/FeatureManifest.cs:140` (`FromBalance`)               |
| Validate wave ordering invariants  | `CivicSurvival/Core/Infrastructure/FeatureManifest.cs:111` (`ValidateWaveOrdering`)      |
| Apply at system registration       | `CivicSurvival/Mod.cs:456` (`SystemRegistrar.RegisterAll(updateSystem, manifest)`)       |

## Wave ordering invariants

`ValidateWaveOrdering` enforces that `Network`, `Arena`, and `ArenaUI`
are configured **together** and in the order
`ArenaUI ≥ Arena ≥ Network`. This is because Arena depends on Network,
and ArenaUI depends on Arena — a misconfiguration would crash on first
load, so the gate fails closed at boot rather than at runtime.

The discipline test `tests/test_release_phases.py::test_wave_ordering_invariant_is_documented`
locks this in.

## Mapping USER_GUIDE phases to waves

The USER_GUIDE mentions four phases:

| Phase       | What ships                                                                      | Wave | Notes                                                                                   |
| ----------- | ------------------------------------------------------------------------------- | ---- | --------------------------------------------------------------------------------------- |
| **Phase 1** | Wave execution, air defense, tutorial, scenario, civic narrative, basic economy | 1    | Default wave; features default to wave 1 when no entry is present in the balance config |
| **Phase 2** | Network topology, Arena, Arena leaderboards, advanced diplomacy                 | 2    | `Network`, `Arena`, `ArenaUI` are the canonical Phase 2 trio                            |
| **Phase 3** | Grid warfare (multi-district cooperation), refugees, mobilization               | 3    | `GridWarfare`, `Refugees`, `Mobilization`                                               |
| **Phase 4** | Cross-domain coordinator features, efficiency telemetry, advanced UI            | 4    | `Efficiency`, `DamageAccounting`, full `UIDomain`                                       |

Any feature can be **preview-only** (waves > currentWave but < sentinel)
so the UI can dim-render it as a roadmap hint. To enable a preview
feature without waiting, raise `currentWave` in the balance config; the
manifest rebuilds at next launch.

## Discipline rules (enforced by `tests/test_release_phases.py`)

The test suite enforces four rules:

1. **All registered domains must have a wave entry.** A domain that
   registers without an explicit wave default to wave 1, which makes
   shipping accidental. The test fails CI if a domain's name (matched
   against the `Register(new XxxDomain())` calls in `Mod.cs`) is missing
   from the wave config — UNLESS it's intentionally listed as a
   non-wave-gated feature (e.g., `Effects`, which is required by
   Phase 1 and cannot be phased out).

2. **Waves must be in `[1, 98]` for shipping features.** Sentinel value
   `99` is reserved for "permanently unavailable"; using it on a
   shipping feature is a configuration bug.

3. **ValidateWaveOrdering must hold.** Network/Arena/ArenaUI triple must
   be present together and ordered (covered by `ValidateWaveOrdering`
   itself; the test re-asserts it for the live config to catch a
   regression in the validator).

4. **Every wave entry must point to a registered domain.** A wave entry
   that names a feature not in `Mod.RegisterFeatures()` is a dead config
   that will never trigger; the test fails CI to surface typos.

## Adding a new feature

```text
1. Register the domain in Mod.RegisterFeatures():  registry.Register(new MyDomain());
2. Add to RemoteBalanceConfig.FeatureGates.Waves:  { "My": 1 }  (or 2, 3, 4 as appropriate)
3. Run:  python -m pytest tests/test_release_phases.py -v
4. Bump the wave as phases ship:  { "My": 2 }  when Phase 2 ships
```

If you forget step 2, the discipline test fails with a precise list of
unregistered domains. If you forget step 1, the test fails with a
precise list of dead wave entries.

## Why waves, not `enum ReleasePhase { Phase1, Phase2, ... }`?

A typed enum forces a code change to add a phase. A wave number is
**data** — the shipping contract is the JSON, not the type system. This
matters because:

- Remote hotfixes can advance a wave without a release
- Preview waves can be tested in-house before public release
- Reverting a wave is a config change, not a rollback
- The same code runs for every player; only the manifest differs

The cost: **discipline**. Every domain must declare its wave, and the
test suite enforces it. This is exactly the kind of discipline that's
worth a 30-second test that runs forever.
