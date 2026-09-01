# Civic Worktree Reconciliation Evidence

**Repository**: `KooshaPari/CivicSurvival-public`  
**Read-only upstream**: `Theorist100/CivicSurvival-public`  
**Evidence base**: `4f34815f4a29be55799c37071db55dcb30e6a2ee`  
**Recorded**: 2026-09-01 UTC  
**Cleanup state**: PENDING

This record proves the disposition of the local Civic worktree estate before
any worktree is removed. It does not authorize branch deletion, ref rewriting,
history cleanup, a WP01 `GO`, or production warfare implementation.

## Protected Boundaries

- The fork is the only writable repository.
- `origin/feat/civic-warfare-program` remains immutable at
  `3bd4431b083101669fc9244e2e09afe182c2b10b`.
- PR #2 was closed unmerged as superseded on 2026-09-01 after its focused
  documentation successor, PR #3, merged. Its source branch remains the
  immutable provenance record and must not be rewritten, deleted, or
  force-pushed.
- No local or remote branch is removed as part of worktree retirement.
- Licensed Windows/CS2 build and runtime evidence remains external to this
  local reconciliation.

## Canonical Main and Hosted Evidence

`4f34815f4a29be55799c37071db55dcb30e6a2ee` is a strict descendant of the
previous `ed78823ee6d29f5aeeb832b2eb75a5cc35b2adb9` snapshot:

```text
ed78823  PR #44  scorecard JSON/Markdown parity
   |
ee8bfc9  PR #46  v0.3.25 and localization regression tests
   |
4f34815  PR #47  dependency-delta metadata-only correction
```

Exact-main hosted runs:

| Workflow            |           Run | Result  |
| ------------------- | ------------: | ------- |
| CI                  | `33465695000` | success |
| Trunk Check         | `33465695003` | success |
| 88-Pillar Scorecard | `33465695006` | success |
| OpenSSF Scorecard   | `33465695008` | success |
| Public audit        | `33465695012` | success |

The 88-Pillar workflow is informational: its exact-main report was `13/88`,
below the configured threshold of 85, even though the workflow itself
completed successfully. OpenSSF Scorecard completed successfully. Neither
workflow conclusion is represented here as Civic merge-readiness or WP01
evidence; the required Civic checks remain the controlling public gate.

PR #41 merged as `1d529c9f5b84192887004cf7ab98dc3cc02c8b29`.
Its archived final-head rollup lacks Kilo Code Review even though current
protection requires it. This is preserved as an audit anomaly; the merge is
not reopened or rewritten. PR #46 had early failing Trunk runs. PR #47
corrected the formatting/dependency-delta surface and its exact-main runs are
green.

## Worktree Disposition

The estate contains one primary checkout and 15 auxiliary worktrees. Fourteen
of the 15 auxiliary worktrees are clean. The sole dirty auxiliary path is
generated Python bytecode:

```text
/private/tmp/CivicSurvival-infisical-pinned-20260830/
  tests/__pycache__/test_infisical_workflow.cpython-314-pytest-9.1.1.pyc
```

The primary checkout contains only this four-file reconciliation change. No
worktree has a lock, unfinished merge, rebase, cherry-pick, revert, bisect,
sequencer, index lock, stash, or active Git operation.

| Worktree                    | HEAD                           | Proof                                          | Disposition                          |
| --------------------------- | ------------------------------ | ---------------------------------------------- | ------------------------------------ |
| Primary checkout            | `75cd9ad` before normalization | PR #41 range-diff and patch equivalence        | retained; normalized to current main |
| `baseline-correct`          | `dc8b83e`                      | tree-identical to PR #36 merge `9a1a8c0`       | retire after checkpoint              |
| `contracts-compat`          | `f002260`                      | tree-identical to PR #21 merge `8caaf30`       | retire after checkpoint              |
| `current-main`              | `755b994`                      | exact historical PR #35 merge                  | retire after checkpoint              |
| `host-evidence`             | `76b8df4`                      | tree-identical to PR #26 merge `d258ae4`       | retire after checkpoint              |
| `infisical-pinned-20260830` | `4d8709a`                      | both unique commits patch-equivalent to PR #42 | retire after generated-only check    |
| `intent`                    | `aeab497`                      | tree-identical to PR #31 merge `f42dab9`       | retire after checkpoint              |
| `main-baseline`             | `1a7a229`                      | exact historical PR #33 merge                  | retire after checkpoint              |
| `mergify`                   | `1a2a2f2`                      | unique commit patch-equivalent to PR #33       | retire after checkpoint              |
| `mergify-final`             | `b23fdac`                      | tree-identical to PR #33 merge `1a7a229`       | retire after checkpoint              |
| `pr23-verify`               | `5bbea6e`                      | ancestor of final PR #23 head                  | retire after checkpoint              |
| `public-pr5`                | `eee5707`                      | tree-identical to PR #5 merge `ad41d7f`        | retire after checkpoint              |
| `scorecard-parity-20260831` | `06edf17`                      | tree-identical to PR #44 merge `ed78823`       | retire after checkpoint              |
| `scorecard-ruff-20260831`   | `ed0ef9f`                      | unique commit patch-equivalent to PR #43       | retire after checkpoint              |
| `wp01-baseline`             | `ac11c0c`                      | tree-identical to PR #34 merge `4d92793`       | retire after checkpoint              |
| `wp02a-audit`               | `079a1a4`                      | tree-identical to PR #35 merge `755b994`       | retire after checkpoint              |

For the historical primary branch, `75cd9ad` is patch-equivalent to
`6032e03`. Range-diff shows its initial action-pin commit was replayed on the
newer base while preserving the concurrently added public-audit test commands.
No novel source remains only on that checkout.

## Machine Proof Methods

The audit used temporary clones and PR refs; it did not update the source
checkout while classifying candidates.

```text
git diff --name-only <pr-head> <merge-sha>
git cherry <final-pr-head> <intermediate-head>
git merge-base --is-ancestor <candidate> <final-pr-head>
git range-diff <historical-series> <accepted-series>
git worktree list --porcelain
git -C <worktree> status --porcelain=v1
git for-each-ref refs/stash
```

Results:

- Nine PR-head/merge pairs returned zero changed paths.
- Every intermediate commit classified by `git cherry` returned `-`.
- `pr23-verify` passed the ancestor check.
- All operation-marker probes returned `none`.
- No stash ref was present.

## Pre-Cleanup Ref Manifest

Captured after fast-forwarding local `main` and creating the reconciliation
branch, but before removing any auxiliary worktree:

| Ref class            | Count | Sorted manifest SHA-256                                            |
| -------------------- | ----: | ------------------------------------------------------------------ |
| Local heads          |    24 | `2c41ecadd61bada621761862f21e2be38b6d7950ee0b77145b0190bb893de35c` |
| Remote-tracking refs |    24 | `62f2cadaa253ae92ed7d1cce96bb31c8f7842f83f1971c9a9388bdc7f338930f` |

Worktree removal must preserve every branch name and every non-advancing SHA.
Advancement of `main`, `origin/main`, and this reconciliation branch is
expected only through the protected PR flow.

## Cleanup Gate

Cleanup may begin only after this evidence is committed, pushed, attached to a
PR, and its initial protected checks pass. Fourteen clean auxiliary worktrees
use ordinary path-specific `git worktree remove`. The Infisical worktree may
use path-specific forced removal only if its complete dirty listing still
equals the single generated `.pyc` above. `git worktree prune` is forbidden.

After cleanup, this record must be updated with actual worktree count, ref
preservation evidence, primary checkout state, and hosted rerun IDs before the
PR merges.

## WP01 Boundary

The checked-in provisional AgilePlus database reports 20 planned work packages
and zero doing, review, done, or blocked records. The canonical MCP service was
healthy when checked on 2026-09-01, but listed no `civic-warfare-program`
feature, work packages, governance result, or audit chain. That service/file
gap is itself unresolved evidence; the local database is not a supported
receipt. WP01 remains `NO-GO` until all of the following are real and linked to
the exact subject commit:

- licensed adapter build;
- CS2 launch/attach smoke;
- artifact hashes and provenance;
- supported AgilePlus evidence receipt;
- successful WP01 verifier result;
- conditional `GO` decision.

No gameplay implementation is authorized by this reconciliation.
