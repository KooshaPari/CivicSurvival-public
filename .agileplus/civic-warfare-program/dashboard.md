# Civic Warfare Program Dashboard

**Generated from**: provisional local AgilePlus DB `.agileplus/civic-warfare-program-v4.db` plus canonical `plan.md`
**Feature state**: planned | **Implementation gate**: closed
**Dated reconciliation snapshot**: `4f34815f4a29be55799c37071db55dcb30e6a2ee`
**Observed fork main / branch base (2026-09-01 09:32 UTC)**: `7f221f897f877aa5b2fea50b5969c67845928c01`
**Canonical MCP state**: healthy service; Civic feature absent; evidence receipt unavailable
**Resume marker**: 2026-09-02 GLM session (Codex `019fab2f-4c10-7770-b288-0e5826ed1ad5` resumed by GLM; Codex resuming in ~4 days). Active branch is `docs/civic-reconciliation-governance-hard-stop-20260901` at `038c56c`. PR #81 is fully CI-green and awaiting Kilo Code Review.

```text
Specification     [##########] 100%  120/120 FRs defined
Research          [##########] 100%  audit + 29 sources + 15 evidence decisions
Architecture      [##########] 100%  contexts, ownership, runtime, failure policy
Data/contracts    [##########] 100%  model + ABI + C header + FlatBuffers draft
DAG/WBS           [##########] 100%  20/20 WPs registered and mapped
Implementation    [..........]   0%  0/120 FRs accepted
Quality gates     [#########.]  90%  AgilePlus evidence PASS (40/40); WP02-A FlatBuffers gate added (4/4 gates); licensed adapter pending
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
WP01 [doing] public audit green; 4/4 gates pass; licensed adapter pending
  -> WP02 [planned] architecture/contracts/ABI (FlatBuffers gate added; native impl gated by WP01)
  -> WP03 [planned] deterministic kernel/replay
  -> WP04 [planned] geography/LOD
  -> {WP05 statecraft, WP14 intelligence (after WP05), WP19 harness}
  -> WP06 economy -> WP07 logistics -> WP08 forces
  -> {WP09 ground, WP10 air, WP11 sea, WP12 defense, WP15 civil}
  -> WP13 operations -> WP16 AI -> {WP17 UI, WP18 campaigns}
  -> WP18 campaigns -> WP19 final validation -> WP20 release
```

## Next Meaningful Work

1. Await Kilo Code Review on PR #81 (fully CI-green); merge after approval.
2. Obtain licensed game-adapter build and launch-smoke evidence on a Windows/CS2 host; attach artifact-hash and provenance to `wp01-go-no-go.md`; re-promote WP01 to GO.
3. After PR #81 lands, prepare a successor WP02-A PR from current `origin/main` with test-first ABI/schema/golden-vector evidence: native-side reader golden vectors, C# deserialization path, end-to-end roundtrip using the Rust test-vector generator.
4. Extend `test_flatbuffers_contract_drift.sh` as the schema grows: every new enum member, struct field, and ABI function needs a corresponding mutation case that proves removal is caught.
5. Resolve the pre-existing C# solution NuGet "Invalid framework identifier" error (out of scope for PR #81).
6. Only after branch-protection governance is verified stable, merge the completed reconciliation record through protection; auto-merge and queueing are prohibited beforehand.
7. ~~Close the AgilePlus evidence-recording gap~~ CLOSED (40/40 evidence); ~~obtain licensed-adapter evidence for WP01~~ pending Windows/CS2 host.
8. WP02-A native ABI/schema boundary work will start only after WP01 acceptance and the new FlatBuffers gate being verified in production.

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
