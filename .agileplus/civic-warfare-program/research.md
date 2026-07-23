# Research: Civic Warfare and Resilient City Program

**Date**: 2026-07-22 | **Mode**: grounded audit and feasibility | **Baseline**: v0.3.24 `0b218074`

Source-level findings are auditable through `research/source-register.csv` and `research/evidence-log.csv`. The upstream release is a single squashed root commit, so changes from v0.3.23 use the prior recorded audit rather than a Git diff.

## Executive Assessment

The project has unusually strong domain vocabulary, single-writer ECS ownership, registry composition, durable intents/outcomes, privacy defaults, localization discipline, and a compelling existing air-defense/economic-survival loop. It is not ready for a warfare expansion branch: the public snapshot cannot reproduce a C# build, has no public C# tests or CI, deliberately omits tools/analyzers/generators, has severe module-size hotspots, and retains version/privacy/dependency inconsistencies.

| Area | Score / 10 | Evidence |
|---|---:|---|
| Architecture | 7.0 | 28 domains, core/domain isolation, FeatureRegistry and ServiceRegistry, single-writer systems |
| Boundaries | 7.0 | Core has no direct domain imports; interfaces exist, but runtime remains one C# project |
| Modularity | 4.0 | 198 handwritten C# files >350 lines, 116 >500, 23 >1000 |
| Build reproducibility | 3.0 | public `dotnet build` fails on missing `/Mod.props`; private tools omitted by design |
| Test maturity | 2.0 | no public C# test project/CI; UI has only 9 Vitest files and 20 lint-rule tests |
| Code quality | 5.0 | 886 warning suppressions, 788 null-forgiving uses, warnings not errors |
| Performance posture | 6.0 | ECS/jobs and ownership discipline are strong; huge systems and unmeasured paths remain |
| Security/privacy | 6.0 | production npm audit clean and diagnostics default off; dev advisories and privacy wording conflict |
| Documentation | 7.0 | extensive public docs, but deliberate non-reproducibility and version drift reduce trust |
| Release maturity | 4.0 | v0.3.24 is a squashed snapshot with inconsistent package versions and no GitHub release history |
| **Overall** | **5.1** | promising architecture, insufficient public proof |

## Current Repository Evidence

- 1,374 C# files and 249,679 total C# LOC. Handwritten filter: 1,357 files, 238,067 LOC.
- Largest systems include `CognitiveUISystem.cs` (1,796), `DonorConferenceSystem.cs` (1,693), `PowerCapacityResolverSystem.cs` (1,686), `ThreatMovementSystem.cs` (1,580), `ThreatDamageSystem.cs` (1,370), and `CivicPrefabInitSystem.cs` (1,368).
- UI contains 378 TS/TSX files and 53,568 LOC; handwritten filter: 359 files, 41,954 LOC. `SettingsPanel.tsx` is 804 lines and `WarRoomContent.tsx` is 679.
- `dotnet build CivicSurvival.sln --no-restore` fails with MSB4019 because `CSII_TOOLPATH`/`Mod.props` is absent. `BUILDING.md` confirms the public snapshot is intentionally non-reproducible and omits private analyzers/source generation plus referenced `Tools/` and `scripts/` paths.
- The UI production dependency audit is clean. The complete dev audit reports seven findings: six high and one low across `@babel/core`, `brace-expansion`, `fast-uri`, `immutable`, `js-yaml`, `undici`, and `vite`.
- Versions disagree: project 0.3.24, manifest 1.0.0, UI mod metadata 0.1.0, inner README 0.9.0-rc.1.
- en-US, uk-UA, and new zh-CN each contain 3,531 scalar leaves with exact key parity.
- Runtime/UI defaults show diagnostics off until opt-in, while `PRIVACY.md` describes optional diagnostics as opt-out. Policy and UI wording must agree.

## Existing Gameplay and Extension Seams

Existing domains already cover AirDefense, Attention, Blackout, Cognitive, Corruption, Countermeasures, Diplomacy, Economics, Engineering, Finance, GridWarfare, Intel, Mobilization, Narrative, NeighborEnvy, Network, Notifications, PowerBackup, PowerGrid, Refugees, Scenario, ShadowEconomy, Spotters, ThreatDamage, ThreatFlight, ThreatUI, Tutorial, and Waves.

The present strategic layer is reusable:

- `GridWarfareDomain` registers enemy simulation, mirror city, counterattack arsenal, player attack, and enemy operation effects.
- `EnemyState`, `EnemyTarget`, `MirrorCitySystem`, `AttackRegistry`, and `PlayerAttackSystem` provide a persistent opposing-city abstraction.
- `IOutboundStrikeService`, `OutboundStrikePayload`, `OutboundArrivalSignal`, `ThreatSpawnSystem`, and `ThreatArrivalSystem` form a durable projectile bridge.
- City budget, crisis economics, war-damage debt, shadow economy, counterattack procurement, air-defense resupply, manpower, grid stress, repair, corruption, donor aid, cognitive warfare, and refugees already make defense depend on the city.

Missing capabilities are structural, not catalog gaps: no ground formations/fronts/terrain capture/occupation; no maritime forces/sea zones/ports/convoys; no geopolitical faction ownership; and no physical multi-modal supply graph. The correct extension retains current strategic systems as adapters/projections while adding a separate operational kernel.

## Architecture Decision

Use a modular monolith with a pure deterministic Rust core and a C#/Unity host. Apply hexagonal architecture at Unity/native/schema/offline-tool boundaries and bounded-context ownership seams, not as interface-per-class ceremony. Use lightweight DDD context boundaries, CQRS-style commands and immutable query projections, functional core/imperative shell, and snapshot-plus-journal replay. Do not blanket event-source every tick, introduce microservices, add a second generic ECS, use actors in authoritative state, or allow dynamic runtime code plugins.

Canonical dependency direction:

```text
TS War Room -> C# command/query facade -> native adapter -> C ABI
                                                       |
Rust headless/FFI -> application ports -> deterministic domain contexts
                                                       |
                       snapshots <- journal <- outcomes/projections
```

Context order is acyclic: identity/geography -> factions/intelligence/economy -> logistics/forces -> operations -> combat -> civil/diplomatic consequences -> projections. Strategic AI reads only faction knowledge projections and emits ordinary commands.

## Build, Borrow, Wrap, or Reject

| Decision | Library/repository | Role and guardrail |
|---|---|---|
| Adopt | Interoptopus | Generate narrow C ABI/C# bindings; opaque handles and owned buffers only |
| Adopt pinned | FlatBuffers | Single-source Rust/C#/TS/Python envelopes; compiler/runtime versions move together |
| Adopt | Serde | Rust internal DTO/config serialization; never expose Rust memory layout |
| Adopt | `fixed` | Authoritative fixed-point quantities wrapped in checked domain newtypes |
| Adopt wrapped | petgraph | Theater/logistics/access graphs; stable domain IDs and sorted traversal |
| Adopt wrapped | rstar | Rebuildable derived spatial index; never persist tree topology |
| Adopt wrapped | bonsai BT | Mission execution only behind a deterministic behavior port |
| Adopt | rand_chacha | Versioned named random streams; no global RNG |
| Adopt | BLAKE3 | Canonical state/replay hashes over sorted serialized state |
| Adopt | zstd under BSD | Snapshot/replay compression after canonical serialization |
| Adopt narrowly | Rayon | Read-only scoring/tiles, stable collection, serial authoritative commit |
| Test tooling | proptest, cargo-fuzz, Criterion | Invariants, decoder/ABI fuzzing, replay differential tests, budgets |
| Offline only | JuMP + HiGHS | Balance, force mix, supply calibration, scenario optimization |
| Advisory only | OR-Tools | Expensive scenario/route experiments whose results enter as validated commands |
| Reference first | OpenRA, Warzone 2100, Freeciv, OpenTTD | Study deterministic replay, bases, diplomacy, logistics; no copying before license ADR |
| Reject runtime | Bevy/Legion ECS | Duplicates Unity ECS and adds scheduling/order/version risk at this scale |
| Reject runtime | current Rust HTN crates | Insufficient maturity; implement a small domain decomposition kernel |
| Reject runtime | neural agent models and live LP/MIP solvers | Opaque, nondeterministic, expensive, and distribution-heavy |

Copyleft is sponsor-acceptable and whole-project relicensing is authorized if warranted. No audited reference currently provides enough direct leverage to justify that cost. GPL code therefore remains reference-only unless a dedicated ADR proves material benefit, ownership, asset compatibility, notice obligations, and the exact relicense plan.

## Polyglot Ownership

| Language | Owned artifact | Production status |
|---|---|---|
| C# | Unity/ECS host, adapters, save lifecycle, presentation, packaging | Shipped |
| Rust | deterministic authoritative simulation, replay, FFI, headless tests | Shipped |
| TypeScript/React | War Room and city UI projections/commands | Shipped |
| Python | scenario authoring, telemetry analysis, data preparation, orchestration | Offline |
| Julia | mathematical optimization, calibration, sensitivity analysis | Offline |
| Zig | reproducible native cross-link and ABI conformance if benchmarked superior | Build-only candidate |
| Mojo | SIMD/GPU research kernels after toolchain experiments | Experimental |
| Nim/Pony/Vale | no unique current ownership; benchmark/provenance research only | Rejected for production |

Every additional language requires an ADR, isolated artifact boundary, pinned toolchain, license/security/distribution proof, and a measured benefit unavailable in the existing stack.

## Delivery and Risk Conclusions

1. WP01 is a hard production-code gate: restore a public audit build, baseline C# tests, CI, version/privacy consistency, and high-risk dependency/module hygiene.
2. WP01-WP03 prove the ABI, deterministic core, schemas, headless replay, geography, and exact LOD conservation before gameplay breadth.
3. Economy/logistics/factions form the shared substrate. Ground, air, sea, fortification, covert, and civil lanes depend on it and can then proceed in parallel.
4. The first native proof sends a FlatBuffers command batch through Interoptopus, runs 10,000 ticks twice, and requires identical BLAKE3 state hashes before graph/AI libraries enter authoritative runtime.
5. UI, configuration, campaigns, verification, documentation, licensing, and release are first-class work packages, not end-of-project cleanup.

## Open Risks (already resolved into plan gates)

- Proprietary CS2 references: public audit build covers game-independent assemblies; installed-game adapter build is a separate smoke lane.
- Native distribution: Windows x64 ships first; fail closed and preserve city saves when native loading/version checks fail.
- Scope: exactly 20 work packages and 100 FRs with staged entry/exit evidence prevent a single unbounded implementation branch.
- Save stability: warfare uses a new forward-only schema; no legacy-development compatibility paths.
- Performance: hierarchical aggregation, stable tables, derived indexes, staggered planning, and explicit budgets are mandatory from the first vertical slice.
