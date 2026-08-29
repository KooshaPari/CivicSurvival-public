# Preserved-Branch Successor Coverage

This ledger reconciles the immutable preservation ref
`origin/feat/civic-warfare-program` (`3bd4431b083101669fc9244e2e09afe182c2b10b`)
against the focused successor PRs. It is a coverage record, not permission to
merge the preserved branch wholesale.

| Preserved content                                                                                                                     | Successor                                       | Status and gate                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.agileplus/civic-warfare-program/**` and the dated session dossier                                                                   | PR #3                                           | Included and validated by the Civic Evidence Gate.                                                                                                    |
| Public ABI, projections, binding validators, and WP01 manifest verifier                                                               | PR #3                                           | Included; local contract/projection tests pass.                                                                                                       |
| CI/Mergify/security workflow hardening                                                                                                | PR #4 (with matching Mergify contract in PR #3) | Included; hosted Security Scan and CI pass; human/default-branch gates remain.                                                                        |
| Public audit runner, contracts build, policy checks, and privacy wording                                                              | PR #5                                           | Included; both hosted `public-audit` jobs pass.                                                                                                       |
| `native/**` source, FlatBuffers compiler setup, and `tests/wp02/**`                                                                   | Future WP02 successor                           | Intentionally deferred until WP01 licensed evidence and a pinned `flatc` toolchain are available. No `native/target/**` build output may be promoted. |
| `agileplus-specs/csv-*`, `CivicSurvival/manifest.json`, UI lockfile, legacy scorecard/trunk workflows, and unrelated release metadata | Separate reconciliation lane                    | Not part of the warfare/ABI/audit successors; preserve on the archive ref and reconcile independently after ownership and provenance review.          |

## Verification commands

From a clean checkout, compare the archive and successor heads without changing
refs:

```text
git diff --name-only origin/main origin/feat/civic-warfare-program
git diff --name-only origin/main <successor-head>
git worktree list --porcelain
```

Any path outside the listed successor scope requires a new focused PR or an
explicit disposition. The archive ref remains immutable evidence.
