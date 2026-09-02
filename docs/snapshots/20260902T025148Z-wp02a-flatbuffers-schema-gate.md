# CivicSurvival WP02-A FlatBuffers Schema Contract Gate Snapshot

- **Date (UTC)**: 2026-09-02T02:51:48Z
- **Branch**: docs/civic-reconciliation-governance-hard-stop-20260901
- **Head commit**: ade737eff1469c5906e6971875a5dc1a840000b9
- **Fork**: KooshaPari/CivicSurvival-public
- **Upstream**: Theorist100/CivicSurvival-public

## Change

`CivicSurvival.PublicAudit/Program.cs` now implements a 4th public-audit
gate, `CheckFlatbuffersSchema()`. The gate validates the warfare program
wire contracts (`.agileplus/civic-warfare-program/contracts/warfare.fbs`
and `civic_warfare.h`) before any native Rust code is written.

### What it validates

| Check                                | Condition                                                                                                                                |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Required enum members (CommandKind)  | All 8 members present (NoOp, SetPolicy, SetBudget, RecruitFormation, SetMission, Negotiate, ConductCovertOperation, RespondToCivilEvent) |
| Required enum members (DecisionCode) | All 4 members present (InsufficientResources, Aborted, Accepted, InProgress)                                                             |
| File identifier                      | Exactly `CSWP`                                                                                                                           |
| Root type                            | Exactly `CommandDispatch`                                                                                                                |
| Required csw\_\* ABI functions       | csw_init, csw_status_into, csw_poll_into, csw_arena_command, csw_warfare_faction_snapshot                                                |
| Proprietary game SDK symbols         | Zero occurrences of ColossalOrder, Colossal, CO DLL, or CO:: in the public header                                                        |

### Anti-drift enforcement

The gate enforces that the wire contract can never be _shrunk_ — enum
members, structs, file_identifier, and ABI functions can only be added,
never removed. Adding members is allowed. Removing or renaming any of the
above is a hard public-audit failure.

## Regression test

`tests/public-audit/test_flatbuffers_contract_drift.sh` proves all 5
mutation cases are caught:

1. Removed `SetMission` from CommandKind enum → audit fail
2. Removed `InsufficientResources` from DecisionCode enum → audit fail
3. Changed `file_identifier` from CSWP → audit fail
4. Removed `csw_status_into` from header → audit fail
5. Injected `#include <ColossalOrder/CitiesSkylinesApi.h>` → audit fail

## Verification

```bash
# 4 gates pass
bash tests/public-audit/test_runner.sh
# -> {"status":"pass","contractsBuild":"pass","localizationParity":"pass","sourceRoots":"pass","flatbuffersSchema":"pass"}

# Regression test catches all 5 drift mutations
bash tests/public-audit/test_flatbuffers_contract_drift.sh
# -> All FlatBuffers contract drift regressions are detected.

# Contracts build unaffected
bash tests/public-audit/test_contracts_build.sh
# -> PASS: contracts build without private toolchain

# AgilePlus evidence recorded
agileplus validate --repo . --db .agileplus/civic-warfare-program-v4.db --feature civic-warfare-program
# -> PASS: Evidence 40/40 passed
```

## Commits (this branch)

- `ade737e` feat(civic): WP02-A FlatBuffers schema contract gate
- `06a14f7` ci(ts): generate package-lock.json to unblock npm ci in CI
- `e29fdc` docs(snapshot): capture WP01 runner portability evidence
- `b1bd262` docs(civic): close AgilePlus evidence gap; WP01 evidence 40/40 PASS

## Program state

- WP01 public-audit lane: green (4 gates)
- WP01 production-warfare gate: still closed (licensed adapter required)
- WP02-A wire contract gate: green (4 gates including flatbuffersSchema)
- WP02-A native implementation: not started (gated by WP01 acceptance)
- AgilePlus evidence: 40/40 PASS

## Hard constraints (unchanged)

- Never shrink the wire contract (enum members, ABI functions, file_identifier)
- Never introduce proprietary game SDK symbols in the public contracts
- Production warfare remains blocked until WP01 is formally accepted
