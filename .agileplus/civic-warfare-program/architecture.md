# Civic Warfare Technical Architecture

## System Shape

The product is a modular monolith split across three shipped artifacts: the existing C#/Unity mod host, a deterministic Rust native library, and the TypeScript/React UI bundle. Offline Python and Julia tools produce validated content and coefficients but never participate in authoritative ticks.

```text
Cities: Skylines II / Unity ECS
          |
   C# observations + commands + saves + projections
          |
   Interoptopus generated C ABI (batched caller-owned buffers)
          |
   Rust application ports
          |
   deterministic domain contexts
          |
   snapshots + command/outcome journal + projections
          |
   C# projection ECS -> TypeScript/React War Room
```

## Dependency Rule

Dependencies point inward. Domain crates import only model, math, rules, and declared upstream contexts. The FFI, filesystem, compression, tracing, Unity, clock, network, and tooling adapters depend on application ports; the domain never imports them. Architecture tests reject cycles and forbidden namespaces/crates.

```text
identity/time -> geography -> factions/intelligence/economy
                                  |
                                  v
                      logistics -> forces
                                  |
                                  v
                 operations -> ground/air/sea/defense
                                  |
                                  v
                  civil/statecraft consequences -> projections
```

Strategic AI reads faction-scoped knowledge projections and emits the same command envelopes as a human. It cannot mutate state directly.

## Context Ownership

| Context             | Sole writer           | Reads                                       | Emits                                                   |
| ------------------- | --------------------- | ------------------------------------------- | ------------------------------------------------------- |
| Identity/Time       | tick reducer          | campaign clock/config                       | tick/revision                                           |
| Geography           | geography reducer     | rules, observations                         | topology/control/weather changes                        |
| Factions/Statecraft | statecraft reducer    | knowledge, economy, civil state             | treaties, access, sovereignty outcomes                  |
| Intelligence        | intelligence reducer  | sources, operations, events                 | knowledge estimates and attribution                     |
| War Economy         | economy reducer       | city observations, contracts, policy        | production, price, budget, construction outcomes        |
| Logistics           | logistics reducer     | graphs, stockpiles, priorities              | deliveries, shortages, losses, causal traces            |
| Force Generation    | force reducer         | population, equipment, training             | readiness, formations, casualty/demobilization outcomes |
| Operations          | operations reducer    | knowledge, forces, logistics, authorization | scheduled mission intents and phases                    |
| Combat              | domain resolvers      | operations, terrain, forces, supply         | losses, control, damage, displacement                   |
| Civil Resilience    | civil reducer         | services, casualties, prices, information   | legitimacy, unrest, actor events, policy consequences   |
| Strategic AI        | command producer only | faction knowledge projections               | ordinary commands and explanations                      |
| Projection/Replay   | projection reducer    | accepted outcomes and canonical state       | immutable snapshots/deltas/hashes                       |

Cross-context changes are next-stage outcomes or next-tick commands; direct writes across owners are forbidden.

## Authoritative Tick

1. Read one immutable C# observation batch at revision R.
2. Decode and bound-check command envelopes; deduplicate by command ID.
3. Validate issuer, expected revision, authority, resources, configuration, and prerequisites.
4. Sort accepted commands by `(scheduled_tick, priority, issuer_id, submitted_tick, command_id)`.
5. Update geography/weather and decay faction knowledge.
6. Resolve statecraft, economy, procurement, construction, and civil policy.
7. Resolve logistics flow and readiness.
8. Advance operations and resolve ground/air/sea/defense interactions.
9. Apply casualties, damage, displacement, legitimacy, unrest, diplomatic, and recovery consequences.
10. Produce coarse durable outcomes, immutable projections, state hash, and diagnostic counters.

No authoritative rule reads wall-clock time, platform math, hash-map order, asynchronous completion order, Unity state during resolution, or an unversioned global RNG.

## Hierarchical Detail

Canonical entities always exist. Detail bubbles materialize tactical representatives for player-proximate, observed, active, or high-consequence regions. Demotion returns representatives to cohort histograms. Both transitions conserve every owned quantity and pending intent. Derived petgraph/rstar/influence structures rebuild from sorted canonical records and are never save identity.

## Persistence and Replay

- Versioned canonical snapshot is the save source of truth.
- Journal stores player/AI commands, validation decisions, and coarse outcomes, not every component mutation.
- Checkpoints contain tick, schema/ABI/rules/RNG versions, sequence high-water mark, content manifest hash, and canonical BLAKE3 state hash.
- Load validates bounds/checksum/version before allocating domain state.
- Replay can rebuild between checkpoints and compare per-context hashes to localize desync.
- Warfare save incompatibility fails closed with an actionable error and preserves the host city save.

## Native Boundary

One create/load call, one batched command submit, one step, and one caller-owned poll per host update. No callbacks into managed code during a Rust tick. Rust owns handles; C# owns input/output buffers. Every fallible function returns a stable error enum; `csw_abi_version` returns the ABI version and `csw_destroy` returns `void`. Panics are contained and converted to fatal runtime status. ABI mismatch disables warfare before state mutation.

## Build/Borrow Policy

Production imports: Interoptopus, pinned FlatBuffers, Serde, `fixed`, petgraph, rstar, bonsai behind a port, rand_chacha, BLAKE3, zstd under BSD, and narrowly constrained Rayon. proptest, cargo-fuzz, Criterion, mutation tests, and schema conformance are required tooling. JuMP/HiGHS and optional OR-Tools remain offline/advisory. GPL strategy repositories remain reference-only until a dedicated relicense ADR is accepted.

## Failure Handling

| Failure                          | Required behavior                                                 |
| -------------------------------- | ----------------------------------------------------------------- |
| native library missing/wrong ABI | disable warfare, retain city play/save, show remediation          |
| malformed command                | reject only command with stable code and reason                   |
| projection buffer too small      | return required length; no partial record                         |
| corrupt snapshot/journal         | reject load before mutation; preserve original data               |
| deterministic mismatch           | stop authoritative advance, write bounded desync bundle           |
| AI planning timeout/budget       | retain prior safe plan or issue explicit hold command             |
| missing content/dependency       | reject campaign start/load with exact IDs and manifest mismatch   |
| offline tool unavailable         | use checked-in validated coefficients/content; runtime unaffected |

## Settings Semantics

- Live: overlays, alerts, UI density, automation notification level, pause behavior.
- Next tick: delegation levels, doctrine priorities, risk tolerance, budget priorities, mission defaults.
- New campaign: faction/settlement scale, enabled warfare domains, rules packs, economy depth, difficulty/resource rules, LOD thresholds that alter canonical modeling.

Dependency validation prevents configurations such as naval invasion without maritime logistics, air missions without air regions/airfields, or autonomous operations with the operations context disabled.
