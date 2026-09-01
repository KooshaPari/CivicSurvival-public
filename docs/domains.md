# Domain Index

This index maps every domain in `CivicSurvival/Domains/` to a one-line description, its registration priority, and the main entry-point class. Sorted by registration priority so the runtime order is also the reading order.

## Reading order (registration priority ascending)

Each domain implements `IFeatureModule` and registers its ECS systems in `Mod.OnLoad` via `SystemRegistrar.RegisterAll`. The priority number controls the order in which `RegisterSystems()` is called; lower numbers run first.

| # | Domain | Priority | Entry point | What it does |
|---|---|---:|---|---|
| 1 | `Blackout` | 2050 | `BlackoutDomain.cs` | Power outages, rolling blackouts, district disconnection |
| 2 | `Engineering` | 2100 | `EngineeringDomain.cs` | Grid stress, threshold operation, equipment wear, disasters |
| 3 | `PowerGrid` | 2105 | `PowerGridDomain.cs` | Electricity production, consumption, shadow trading |
| 4 | `Mobilization` | 2150 | `MobilizationDomain.cs` | Manpower management for AA and military operations |
| 5 | `ShadowEconomy` | 2151 | `ShadowEconomyDomain.cs` | Shadow wallet, offshore accounts, power-trading UI |
| 6 | `Economics` | 2200 | `EconomyDomain.cs` | Crisis economics, donor funds |
| 7 | `Finance` | 2210 | `FinanceDomain.cs` | War damage costs, debt management |
| 8 | `Corruption` | 2220 | `CorruptionDomain.cs` | Corruption schemes, shadow reputation, district modernization |
| 9 | `Countermeasures` | 2240 | `CountermeasuresDomain.cs` | Journalists, police investigations, anti-corruption |
| 10 | `NeighborEnvy` | 2250 | `NeighborEnvyDomain.cs` | Citizens jealous of powered neighbors |
| 11 | `Diplomacy` | 2270 | `DiplomacyDomain.cs` | Donor conferences, crisis monitoring, international scandals |
| 12 | `Scenario` | 2300 | `ScenarioDomain.cs` | State machine, intro, crisis, milestones |
| 13 | `Tutorial` | 2310 | `TutorialDomain.cs` | Tutorial modals and guidance |
| 14 | `Attention` | 2400 | `AttentionDomain.cs` | World shock, exodus |
| 15 | `ThreatUI` | 2503 | `ThreatUIDomain.cs` | Identification, audio, UI for threat display |
| 16 | `ThreatFlight` | 2501 | `ThreatFlightDomain.cs` | Drone/ballistic movement, obstacle avoidance, render sync |
| 17 | `ThreatDamage` | 2502 | `ThreatDamageDomain.cs` | Arrival detection, debris, damage application |
| 18 | `AirDefense` | 2510 | `AirDefenseDomain.cs` | AA installations, interception, ammo, tracers |
| 19 | `Intel` | 2512 | `IntelDomain.cs` | Tension level, price multiplier, insider purchase |
| 20 | `Spotters` | 2514 | `SpottersDomain.cs` | OSINT spotter network spawn, simulation, SBU countermeasures |
| 21 | `Waves` | 2520 | `WavesDomain.cs` | Wave execution, spawn, targeting, cleanup |
| 22 | `Cognitive` | 2550 | `CognitiveDomain.cs` | Mental health and propaganda systems |
| 23 | `Notifications` | 2590 | `NotificationsDomain.cs` | Notification rendering and display |
| 24 | `Narrative` | 2600 | `NarrativeDomain.cs` | Story characters and event resolvers |
| 25 | `Refugees` | 2700 | `RefugeesDomain.cs` | Spawn, migration, integration |
| 26 | `GridWarfare` | 2800 | `GridWarfareDomain.cs` | Enemy simulation, player attacks, city stability |
| 27 | `Network` | 2850 | `NetworkDomain.cs` | Global news, online stats, server communication |
| 28 | `PowerBackup` | 2970 | `PowerBackupDomain.cs` | Generators, batteries, backup power distribution |

## Alphabetical quick reference

For when you know the name but not the priority:

| Domain | Description |
|---|---|
| `AirDefense` | AA installations, interception, ammo, tracers |
| `Attention` | World shock, exodus |
| `Blackout` | Power outages, rolling blackouts, district disconnection |
| `Cognitive` | Mental health and propaganda systems |
| `Corruption` | Corruption schemes, shadow reputation, district modernization |
| `Countermeasures` | Journalists, police investigations, anti-corruption |
| `Diplomacy` | Donor conferences, crisis monitoring, international scandals |
| `Economics` | Crisis economics, donor funds |
| `Engineering` | Grid stress, threshold operation, equipment wear, disasters |
| `Finance` | War damage costs, debt management |
| `GridWarfare` | Enemy simulation, player attacks, city stability |
| `Intel` | Tension level, price multiplier, insider purchase |
| `Mobilization` | Manpower management for AA and military operations |
| `Narrative` | Story characters and event resolvers |
| `NeighborEnvy` | Citizens jealous of powered neighbors |
| `Network` | Global news, online stats, server communication |
| `Notifications` | Notification rendering and display |
| `PowerBackup` | Generators, batteries, backup power distribution |
| `PowerGrid` | Electricity production, consumption, shadow trading |
| `Refugees` | Spawn, migration, integration |
| `Scenario` | State machine, intro, crisis, milestones |
| `ShadowEconomy` | Shadow wallet, offshore accounts, power-trading UI |
| `Spotters` | OSINT spotter network spawn, simulation, SBU countermeasures |
| `ThreatDamage` | Arrival detection, debris, damage application |
| `ThreatFlight` | Drone/ballistic movement, obstacle avoidance, render sync |
| `ThreatUI` | Identification, audio, UI for threat display |
| `Tutorial` | Tutorial modals and guidance |
| `Waves` | Wave execution, spawn, targeting, cleanup |

## Functional grouping

**Power and infrastructure**
- `PowerGrid` — the source of truth for electricity production and consumption
- `Blackout` — outage events; consumes `PowerGrid` data
- `Engineering` — grid stress, equipment wear, disasters
- `PowerBackup` — generators, batteries (read after Efficiency so the generator-efficiency pipeline is complete)
- `Mobilization` — manpower for power-related ops

**Economy and finance**
- `Economics` — crisis economics, donor funds
- `Finance` — war damage costs, debt
- `ShadowEconomy` — shadow wallet, offshore trading
- `Corruption` — schemes, district modernization (Phase 2)

**Society**
- `Cognitive` — mental health, propaganda
- `Countermeasures` — journalists, police
- `NeighborEnvy` — civic jealousy
- `Narrative` — characters, events
- `Refugees` — migration
- `Diplomacy` — international

**Threats (registered as separate domains for ordering control)**
- `ThreatUI` — identification, audio, UI
- `ThreatFlight` — movement, avoidance, render
- `ThreatDamage` — arrival detection, debris
- `Waves` — wave orchestration
- `AirDefense` — AA installations
- `Intel` — tension, price multiplier
- `Spotters` — OSINT network
- `GridWarfare` — enemy simulation

**Meta and lifecycle**
- `Scenario` — state machine (intro, crisis, milestones)
- `Tutorial` — onboarding modals
- `Attention` — world shock, exodus
- `Notifications` — notification rendering
- `Network` — global news, server comms

## How to add a new domain

1. Create `CivicSurvival/Domains/<Name>/<Name>Domain.cs` implementing `IFeatureModule`.
2. Add `using CivicSurvival.Domains.<Name>;` to `CivicSurvival/Mod.cs`.
3. Pick a priority: insert your domain between existing priorities without conflicts; explain in the summary why you need that order.
4. Add a one-line entry to `docs/domains.md` (this file).
5. Add a wave entry to `build-evidence/feature-gates.sample.json` (see `tests/test_release_phases.py`).
6. Add localization keys; the discipline test enforces parity across all 3 locales.
7. If your domain has a `.Serialization.cs` partial, follow `docs/save-format.md`.
8. If your domain has settings, add a tooltip key in all 3 locales (`docs/tutorial-help-portal-audit.md`).

## Verification

This index is data-driven. The discipline test `tests/test_release_phases.py` validates that every `using CivicSurvival.Domains.X;` import in `Mod.cs` has a corresponding entry here. A drift between this file and the codebase fails CI.