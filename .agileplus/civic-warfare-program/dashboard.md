# Civic Warfare Program Dashboard

**Generated from**: AgilePlus DB `.agileplus/civic-warfare-program-v4.db` plus canonical `plan.md`
**Feature state**: planned | **Implementation gate**: closed | **Baseline**: v0.3.24 `0b218074`

```text
Specification     [##########] 100%  120/120 FRs defined
Research          [##########] 100%  audit + 29 sources + 15 evidence decisions
Architecture      [##########] 100%  contexts, ownership, runtime, failure policy
Data/contracts    [##########] 100%  model + ABI + C header + FlatBuffers draft
DAG/WBS           [##########] 100%  20/20 WPs registered and mapped
Implementation    [..........]   0%  0/120 FRs accepted
Quality gates     [######....]  60%  public audit green; licensed adapter/evidence recording pending
```

## Live WP State

| State | Count |
|---|---:|
| planned | 20 |
| doing | 0 |
| review | 0 |
| done | 0 |
| blocked | 0 |

## Current DAG

```text
WP01 [review] public audit green; formal evidence and licensed adapter pending
  -> WP02 [planned] architecture/contracts/ABI
  -> WP03 [planned] deterministic kernel/replay
  -> WP04 [planned] geography/LOD
  -> {WP05 statecraft, WP14 intelligence, WP19 harness}
  -> WP06 economy -> WP07 logistics -> WP08 forces
  -> {WP09 ground, WP10 air, WP11 sea, WP12 defense, WP15 civil}
  -> WP13 operations -> WP16 AI -> {WP17 UI, WP18 campaigns}
  -> WP19 final validation -> WP20 release
```

## Next Meaningful Work

1. Close the AgilePlus evidence-recording gap and obtain licensed adapter evidence for WP01.
2. Begin WP02-A native ABI/schema boundary work behind the conditional gate.

## Refresh Commands

```sh
agileplus --repo "$PWD" --db "$PWD/.agileplus/civic-warfare-program-v4.db" list
agileplus dashboard --db "$PWD/.agileplus/civic-warfare-program-v4.db" --json
agileplus validate --repo "$PWD" --db "$PWD/.agileplus/civic-warfare-program-v4.db" --feature civic-warfare-program --force
```

The installed CLI's inferred dependencies are false positives caused by broad research-text file-scope extraction. `plan.md` is the reviewed canonical DAG until AgilePlus supports dependency overrides; SQLite remains canonical for feature/WP state counts.
