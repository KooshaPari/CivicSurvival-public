# Civic Warfare Program Dashboard

**Generated from**: provisional local AgilePlus DB `.agileplus/civic-warfare-program-v4.db` plus canonical `plan.md`
**Feature state**: planned | **Implementation gate**: closed
**Dated reconciliation snapshot**: `4f34815f4a29be55799c37071db55dcb30e6a2ee`
**Observed fork main / branch base (2026-09-01 09:32 UTC)**: `7f221f897f877aa5b2fea50b5969c67845928c01`
**Canonical MCP state**: healthy service; Civic feature absent; evidence receipt unavailable

```text
Specification     [##########] 100%  120/120 FRs defined
Research          [##########] 100%  audit + 29 sources + 15 evidence decisions
Architecture      [##########] 100%  contexts, ownership, runtime, failure policy
Data/contracts    [##########] 100%  model + ABI + C header + FlatBuffers draft
DAG/WBS           [##########] 100%  20/20 WPs registered and mapped
Implementation    [..........]   0%  0/120 FRs accepted
Quality gates     [######....]  60%  public audit green; licensed adapter/evidence recording pending
Reconciliation    [########..]  80%  equivalence proven; protected record and local cleanup pending
```

## Provisional Local WP State

| State   | Count |
| ------- | ----: |
| planned |    20 |
| doing   |     0 |
| review  |     0 |
| done    |     0 |
| blocked |     0 |

## Current DAG

```text
WP01 [planned] public audit green; formal evidence and licensed adapter pending
  -> WP02 [planned] architecture/contracts/ABI
  -> WP03 [planned] deterministic kernel/replay
  -> WP04 [planned] geography/LOD
  -> {WP05 statecraft, WP14 intelligence (after WP05), WP19 harness}
  -> WP06 economy -> WP07 logistics -> WP08 forces
  -> {WP09 ground, WP10 air, WP11 sea, WP12 defense, WP15 civil}
  -> WP13 operations -> WP16 AI -> {WP17 UI, WP18 campaigns}
  -> WP18 campaigns -> WP19 final validation -> WP20 release
```

## Next Meaningful Work

1. Commit and push the corrective evidence, and attach it to the worktree-reconciliation successor PR.
2. Require all protected checks plus substantive CodeRabbit and Kilo reviews to pass before cleanup.
3. Complete only the proven-safe local cleanup without deleting refs.
4. Record the actual post-cleanup worktree count, ref-preservation evidence, primary-checkout state, and hosted rerun IDs on the successor branch.
5. Merge the completed reconciliation record through protection.
6. Close the AgilePlus evidence-recording gap and obtain licensed-adapter evidence for WP01.
7. Begin WP02-A native ABI/schema boundary work only after WP01 acceptance.

## Refresh Commands

```sh
agileplus --repo "$PWD" --db "$PWD/.agileplus/civic-warfare-program-v4.db" list
agileplus dashboard --db "$PWD/.agileplus/civic-warfare-program-v4.db" --json
agileplus validate --repo "$PWD" --db "$PWD/.agileplus/civic-warfare-program-v4.db" --feature civic-warfare-program --force
```

The installed CLI's inferred dependencies are false positives caused by broad
research-text file-scope extraction. `plan.md` is the reviewed canonical DAG
until AgilePlus supports dependency overrides. The local SQLite counts are a
planning snapshot, not canonical engine state or WP01 evidence; the canonical
MCP service must first receive and verify the Civic feature and its evidence.
