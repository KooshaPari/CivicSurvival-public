# ADR-0004: Domain Priority and Initialization Order Contract

- Status: Accepted
- Date: 2026-09-01
- Decision owner: program coordinator
- Scope: `CivicSurvival/Domains/*Domain.cs`, `CivicSurvival/Mod.cs`, `docs/domains.md`

## Context

The 28 domain classes each declare `public const int PRIORITY = N;` (or
`private const int PRIORITY = N;` exposed via a `Priority` property) and
are loaded in ascending priority order at Mod startup. The runtime
expects this contract; the README and onboarding material assume it.
Until now, the contract was implicit. A domain that changed its priority
without rationale could shift the load order, causing silent
initialization bugs (e.g. a domain that reads settings before the
Settings domain loads, or telemetry bootstrap firing before consent
storage is ready).

Inspection of the current 28 domains shows the convention is:
- Range: 2050..2970 (gameplay tier is `>= 2000`)
- Increments: 1, 5, 10, 50 (decade boundaries mark tier transitions)
- Tier groupings by decade:
  - 2000s — base gameplay (Blackout=2050)
  - 2100s — power + mobilization (PowerGrid=2105, Mobilization=2150)
  - 2200s — economy + finance + soft state (Economics=2200,
    Corruption=2220, Countermeasures=2240, Diplomacy=2270)
  - 2300s — scenario + tutorial
  - 2400s — attention / world-shock / cognitive
  - 2500s — threats + countermeasure machinery
  - 2600s — narrative
  - 2700s — refugees
  - 2800s — meta systems (GridWarfare=2800, Network=2850)
  - 2900s — backups (PowerBackup=2970)
- All current priorities are unique. A tie causes non-determinism in
  load order, which manifests as flaky tests.

This ADR makes the contract explicit and gives it a discipline test.

## Decision

Adopt the following invariants for `PRIORITY` in any `*Domain.cs`:

1. **Numeric range**: 1000..9999 inclusive. The 2000s tier is gameplay,
   the 3000s tier is reserved for UI-only domains, and the 9000s tier
   is reserved for opt-in experimental domains that must not auto-load.
2. **Unique**: no two domains share a priority value. Ties cause non-
   determinism.
3. **Tier alignment**: the priority number's decade (priority / 10)
   must indicate the tier. Two domains with the same decade prefix are
   in the same tier; the units digit orders within the tier.
4. **Doc-tracked**: every domain's priority must appear in
   `docs/domains.md` (the domain discovery index) AND this ADR with
   the same value declared in source.
5. **No sentinel value abuse**: `priority = 0` is forbidden (it would
   load first, before everything else, and break the contract). To opt
   a domain out of the auto-load path, use the 9000s range as the
   documented escape hatch.

A discipline test (`tests/test_domains_priority_contract.py`) enforces
all five invariants. The test fails CI on any single drift direction:
(declaration without doc entry, doc entry without declaration, priority
tie, tier misalignment, out-of-range value).

## Current Priority Table (canonical, ascending load order)

This table is the source-of-truth that `tests/test_domain_registration_discipline.py::test_domain_priority_values_match_adr_0004` cross-checks against the runtime `PRIORITY = N;` declarations in each `*Domain.cs`. Any drift between source and this table is a CI failure.

| Domain | PRIORITY | Tier |
|--------|---------:|------|
| Blackout | 2050 | 2000s — base gameplay |
| Engineering | 2100 | 2100s — power + mobilization |
| PowerGrid | 2105 | 2100s — power + mobilization |
| Mobilization | 2150 | 2100s — power + mobilization |
| ShadowEconomy | 2151 | 2100s — power + mobilization |
| Finance | 2210 | 2200s — economy + finance + soft state |
| Corruption | 2220 | 2200s — economy + finance + soft state |
| Countermeasures | 2240 | 2200s — economy + finance + soft state |
| NeighborEnvy | 2250 | 2200s — economy + finance + soft state |
| Diplomacy | 2270 | 2200s — economy + finance + soft state |
| Scenario | 2300 | 2300s — scenario + tutorial |
| Tutorial | 2310 | 2300s — scenario + tutorial |
| Attention | 2400 | 2400s — attention / world-shock / cognitive |
| ThreatFlight | 2501 | 2500s — threats + countermeasure machinery |
| ThreatDamage | 2502 | 2500s — threats + countermeasure machinery |
| ThreatUI | 2503 | 2500s — threats + countermeasure machinery |
| AirDefense | 2510 | 2500s — threats + countermeasure machinery |
| Intel | 2512 | 2500s — threats + countermeasure machinery |
| Spotters | 2514 | 2500s — threats + countermeasure machinery |
| Waves | 2520 | 2500s — threats + countermeasure machinery |
| Cognitive | 2550 | 2500s — threats + countermeasure machinery |
| Notifications | 2590 | 2500s — threats + countermeasure machinery |
| Narrative | 2600 | 2600s — narrative |
| Refugees | 2700 | 2700s — refugees |
| GridWarfare | 2800 | 2800s — meta systems |
| Network | 2850 | 2800s — meta systems |
| PowerBackup | 2970 | 2900s — backups |
## Consequences

- The 28 current domains are now subject to a regression test on every
  PR touching a domain file or `docs/domains.md`. A contributor adding
  a new domain must:
  1. Pick a priority in an unused slot within the appropriate tier.
  2. Declare it in the new `*Domain.cs`.
  3. Add a row to `docs/domains.md`.
  4. Register the domain in `Mod.cs`.
  5. Add a wave entry in the sample balance config.
  Without all five steps, the discipline test fails with the exact
  missing step named.
- The tier convention (priority decade = tier) makes the load order
  visible at a glance. Reading the priority column in
  `docs/domains.md` shows the registration order AND the tier
  grouping simultaneously.
- Future contributors wanting to opt a domain out of the auto-load
  path (e.g. for A/B testing) can declare `priority = 9000` and the
  domain will not be loaded. This is the documented escape hatch.

## Verification References

- `tests/test_domains_priority_contract.py` -- the 5-case discipline test
- `docs/domains.md` -- the index this contract binds
- `tests/test_domains_index_discipline.py` -- the index-consistency
  companion test
- ADR-0001 -- civic program governance (parent of all ADRs)
- ADR-0003 -- source generator publication strategy (sibling concern:
  generators can read PRIORITY and emit registration code)
