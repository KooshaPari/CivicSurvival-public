# Civic Warfare and Resilient City Program - Delivery Plan

**Feature**: `civic-warfare-program` | **State**: planned | **Work packages**: 20
**Operational truth**: `.agileplus/civic-warfare-program-v4.db`
**Specification truth**: this directory and its Git history

## Delivery Policy

WP01 is a hard gate: WP02-WP20 may perform research, design, tests, schemas, and isolated benchmarks, but no production warfare behavior merges until the public audit build and baseline tests, licensed adapter build and launch smoke, artifact hashes/provenance, and supported AgilePlus evidence recording all pass. Each WP uses test-first implementation, files target <=350 lines and never exceed 500, updates all callers in one change, removes superseded paths, and produces machine-readable requirement evidence.

## Program DAG

```text
WP01 Audit/build gate
  |
WP02 Architecture/contracts/ABI
  |
WP03 Deterministic kernel/replay
  |
WP04 Geography/LOD
  +--------------------+------------------+
  |                    |                  |
WP05 Factions       WP14 Intelligence   WP19 Validation harness
  |                    |                  |
WP06 War economy ------+                  |
  |                                       |
WP07 Logistics ---------------------------+
  |
WP08 Forces/mobilization
  +--------+---------+---------+---------+---------+
  |        |         |         |         |         |
WP09     WP10      WP11      WP12      WP15      WP18
Ground   Air       Sea       Defense   Civil     Campaigns
  |        |         |         |         |         |
  +--------+---------+----+----+---------+---------+
                         |
                       WP13 Joint operations
                         |
                       WP16 Strategic AI/autonomy
                         |
                       WP17 War Room/UI/QoL
                         |
                       WP20 Docs/license/release
```

WP19-foundation starts after WP02 and continuously gates every lane; its final acceptance depends on WP01-WP18. Only the named WP17 projection-primitives, WP18 authoring-tools, and WP19 harness-foundation scopes may advance early; their parent work packages remain incomplete until their full dependencies pass. WP17 completes only after gameplay projections are stable. WP18 scenario tooling begins after WP02/WP03 and completes after domain rules exist.

## Execution Waves

| Wave | Work packages                | Entry condition                            | Exit evidence                                              |
| ---: | ---------------------------- | ------------------------------------------ | ---------------------------------------------------------- |
|    0 | WP01                         | fork and baseline available                | public audit build, tests, CI, signed go/no-go             |
|    1 | WP02                         | WP01 pass                                  | ABI spike, schemas, architecture tests, ownership contract |
|    2 | WP03                         | WP02 pass                                  | duplicate 10,000-tick hashes, snapshot/journal round trip  |
|    3 | WP04                         | WP03 pass                                  | geography graph and LOD conservation properties            |
|   3a | WP19-foundation              | WP02 pass                                  | validation ingest and contract harness                     |
|    4 | WP05, WP14                   | WP04; WP05 respectively                    | faction/intel vertical slices                              |
|    5 | WP06                         | WP05 model stable                          | city procurement/construction vertical slice               |
|    6 | WP07                         | WP06 resource contracts stable             | end-to-end physical supply causal trace                    |
|    7 | WP08                         | WP05-WP07 pass                             | mobilization/readiness/population conservation             |
|    8 | WP09, WP10, WP11, WP12, WP15 | WP08 pass; lane-specific assets            | deterministic domain scenario suites                       |
|    9 | WP13, WP16                   | combat/statecraft/civil projections stable | joint operation and explainable AI suites                  |
|   10 | WP17, WP18                   | projection and rules contracts stable      | accessible UI flows and all campaign presets               |
|   11 | WP19-final, WP20             | WP01-WP18 accepted                         | governance validation and reproducible release dossier     |

## Work Package Registry

| WP   | Lane                        | Requirements    | Entry dependencies           | Completion proof                                | Effort |
| ---- | --------------------------- | --------------- | ---------------------------- | ----------------------------------------------- | -----: |
| WP01 | Public audit build          | FR-001..005,101 | none                         | fresh clone build/test/CI and go-no-go report   | 2-4 ew |
| WP02 | Architecture/contracts/ABI  | FR-006..010,102 | WP01                         | ABI/schema conformance and dependency tests     | 3-5 ew |
| WP03 | Deterministic kernel/replay | FR-011..015,103 | WP02                         | replay hashes, fuzzed restore, golden vectors   | 4-6 ew |
| WP04 | Geography/LOD               | FR-016..020,104 | WP03                         | conservation and equivalent-outcome tests       | 4-6 ew |
| WP05 | Factions/statecraft         | FR-021..025,105 | WP04                         | diplomacy/sovereignty scenario suite            | 4-6 ew |
| WP06 | War economy/construction    | FR-026..030,106 | WP02,WP04,WP05               | guns-butter and physical-construction scenarios | 5-8 ew |
| WP07 | Logistics/sustainment       | FR-031..035,107 | WP03,WP04,WP06               | graph conservation and shortage explanations    | 5-8 ew |
| WP08 | Mobilization/forces         | FR-036..040,108 | WP05,WP06,WP07               | population/equipment/readiness conservation     | 4-6 ew |
| WP09 | Ground warfare              | FR-041..045,109 | WP04,WP07,WP08               | ground invariant and reference battle suite     | 5-8 ew |
| WP10 | Air/missile warfare         | FR-046..050,110 | WP04,WP07,WP08               | generalized existing-AA and air scenario suite  | 4-7 ew |
| WP11 | Maritime/littoral           | FR-051..055,111 | WP04,WP07,WP08               | convoy/blockade/amphibious scenario suite       | 4-7 ew |
| WP12 | Fortification/home defense  | FR-056..060,112 | WP04,WP06,WP07,WP08          | layered city-defense and recovery suite         | 4-7 ew |
| WP13 | Joint operations/invasions  | FR-061..065,113 | WP05,WP07,WP08,WP09-WP12     | complete joint-operation lifecycle suite        | 4-7 ew |
| WP14 | Intelligence/covert action  | FR-066..070,114 | WP04,WP05                    | fog/deception/attribution scenario suite        | 4-6 ew |
| WP15 | Civil resilience/unrest     | FR-071..075,115 | WP05-WP08,WP14               | non-dominant response and civil-state suite     | 4-7 ew |
| WP16 | Strategic AI/autonomy       | FR-076..080,116 | WP03-WP08,WP13-WP15          | non-cheating league and explanation suite       | 5-8 ew |
| WP17 | War Room/UI/QoL             | FR-081..085,117 | WP02,WP04-WP08,WP13-WP16     | accessible/localized/performance UI journeys    | 5-8 ew |
| WP18 | Campaigns/rules/config      | FR-086..090,118 | WP02-WP08,WP13-WP16          | three presets and content validation            | 4-6 ew |
| WP19 | Verification/security/perf  | FR-091..095,119 | starts WP02; exits WP01-WP18 | machine-readable complete evidence graph        | 5-8 ew |
| WP20 | Docs/license/release        | FR-096..100,120 | WP01-WP19                    | reproducible package and signed dossier         | 3-5 ew |

`ew` means engineering-weeks of effort, not calendar duration. With five implementation lanes after WP08, estimated total is 78-123 engineering-weeks and 28-44 calendar weeks; rebaseline from measured WP01-WP03 throughput.

## Critical Path and Parallelism

Critical path: `WP01 -> WP02 -> WP03 -> WP04 -> WP05 -> WP06 -> WP07 -> WP08 -> max(WP09,WP10,WP11,WP12,WP15) -> WP13 -> WP16 -> WP17 -> WP19-final -> WP20`.

Safe parallel sets:

- WP05 and WP14 after WP04.
- WP09, WP10, WP11, WP12, and WP15 after their shared substrate passes.
- WP17 projection primitives, WP18 authoring tools, and WP19 harness-foundation may advance early behind stable contracts; no full-WP completion or downstream implementation is implied.
- Offline Julia/Python calibration may run beside all runtime lanes but may only contribute versioned coefficients/content.

## Progress Contract

SQLite WP states are `planned -> doing -> review -> done` with `blocked` as an exception. A lane may enter `doing` only when its canonical DAG dependencies are done, except the explicitly named foundation scopes (`WP17.projection-primitives`, `WP18.authoring-tools`, `WP19.harness-foundation`) after WP02. Program progress is weighted by accepted requirements, not time spent:

```text
wp_progress = accepted_FRs / 6
program_progress = accepted_FRs / 120
quality_progress = passed_required_gates / total_required_gates
```

Every transition records actor, timestamp, commit/PR, tests, artifacts, performance evidence, review result, and prior audit hash. `dashboard.md` is regenerated from SQLite/traceability evidence; percentages are never hand-edited.

## Definition of Done

A WP is done only when all six FRs have evidence, tests are green at required scope, architecture and file-size policies pass, docs/contracts are current, security/license changes are reviewed, performance does not regress beyond budget, and its downstream contract is versioned. The program ships only after WP20 verifies all 120 FRs and 20 quality requirements.
