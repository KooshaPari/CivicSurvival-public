# Civic Warfare Program WBS and Live Task Registry

This registry is the human-readable WBS. AgilePlus SQLite is operational truth; individual work-package prompts live in `tasks/`.

| WP   | Deliverable groups                                                                          | Parallel marker | State   | Dependencies             |
| ---- | ------------------------------------------------------------------------------------------- | --------------- | ------- | ------------------------ |
| WP01 | audit solution; C# tests; CI; metadata/privacy/deps; module gate; go/no-go                  | -               | planned | -                        |
| WP02 | Rust workspace; ABI; FlatBuffers; command protocol; architecture tests; boundary dossier    | -               | planned | WP01                     |
| WP03 | fixed ticks; pipeline; snapshots/journal; replay; deterministic parallelism; golden vectors | -               | planned | WP02                     |
| WP04 | geography; networks; LOD selector; conservation; influence layers; equivalence tests        | -               | planned | WP03                     |
| WP05 | factions; treaties; negotiation; sovereignty; context outcomes; statecraft tests            | P               | planned | WP04                     |
| WP06 | goods; firms/contracts; budget competition; construction; externalities; balance tests      | -               | planned | WP02,WP04,WP05           |
| WP07 | physical graph; throughput; consumption; convoy/interdiction; causal trace; properties      | -               | planned | WP03,WP04,WP06           |
| WP08 | recruitment; force model; lifecycle; casualties; mobilization; cohort tests                 | -               | planned | WP05,WP06,WP07           |
| WP09 | ground resolver; capabilities; orders; control; civilians; scenarios                        | P               | planned | WP04,WP07,WP08           |
| WP10 | air model; missions; detection; existing AA integration; bases; scenarios                   | P               | planned | WP04,WP07,WP08           |
| WP11 | naval model; missions; contact; ports; economic coupling; scenarios                         | P               | planned | WP04,WP07,WP08           |
| WP12 | defenses; properties; plans; civil defense; city effects; layouts                           | P               | planned | WP04,WP06,WP07,WP08      |
| WP13 | operation entity; operation types; invasion gates; command UI; forecasts; lifecycle tests   | -               | planned | WP05,WP07-WP12           |
| WP14 | knowledge; collection; agents; terrorism; fog; uncertainty tests                            | P               | planned | WP04,WP05                |
| WP15 | unrest drivers; event ladder; actors; responses; corruption; non-dominance tests            | P               | planned | WP05-WP08,WP14           |
| WP16 | HTN; utility; fairness; delegation; constraints; decision league                            | -               | planned | WP03-WP08,WP13-WP15      |
| WP17 | dual views; overlays; rosters/QoL; accessibility; localization; UI journeys                 | P               | planned | WP02,WP04-WP08,WP13-WP16 |
| WP18 | presets; rules packs; registry; scale; scenario tools; content validation                   | P               | planned | WP02-WP08,WP13-WP16      |
| WP19 | test matrix; determinism; budgets; fuzz/failure; telemetry; evidence export                 | P               | planned | starts WP02; exits all   |
| WP20 | docs; versions; provenance; packaging; release gate; signed dossier                         | -               | planned | WP01-WP19                |

## Per-WP Mandatory Task Sequence

1. Confirm entry evidence and affected ownership boundaries.
2. Write failing unit/property/contract tests for the FR slice.
3. Implement the smallest complete domain change without placeholders or compatibility shims.
4. Run focused tests and deterministic replay checks.
5. Integrate adapters/projections and run contract/integration tests.
6. Run architecture, file-size, lint, security/license, localization, and performance gates.
7. Update docs, schema versions, requirement evidence, and AgilePlus state.
8. Independent code review, fix-forward loop, commit, push, and Airlock snapshot.

## Evidence Record Required Per FR

`FR ID -> WP -> implementation paths -> test IDs -> command/output hash -> benchmark/security/license evidence -> review -> commit/PR -> acceptance timestamp`.

## Current Counts

- Requirements: 120 planned, 0 accepted.
- Quality requirements: 20 planned, 0 accepted.
- Work packages: 20 planned, 0 working, 0 review, 0 done.
- Implementation gate: closed until WP01 is done.
