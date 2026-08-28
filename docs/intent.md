# CivicSurvival Intent and Delivery Boundary

## Purpose

CivicSurvival is a public, auditable foundation for a city-survival and
grand-theater warfare simulation. The city economy, population,
infrastructure, diplomacy, intelligence, logistics, civil legitimacy, and
military operations must remain explainable and deterministic. The current
repository records the program intent and contracts; it is not an installed
Cities: Skylines II distribution.

The authoritative program feature is `civic-warfare-program`. Its checked-in
AgilePlus artifacts live under `.agileplus/civic-warfare-program/` and define
120 functional requirements (`FR-001` through `FR-120`), 20 quality
requirements (`QR-001` through `QR-020`), and 20 ordered work packages.

## Directives

- Do not merge production warfare behavior until WP01 is accepted.
- Keep Rust as the deterministic theater authority behind the narrow C ABI;
  C# owns game integration and saves; TypeScript/React owns UI and tools.
- Use one canonical resource/rules model for detailed and aggregate
  simulation. Promotion and demotion must conserve state exactly.
- Keep the functional core deterministic: fixed ticks, stable IDs and
  ordering, explicit random streams, snapshots, command/outcome journal, and
  replay hashes.
- Treat AI as a command producer constrained by faction-scoped knowledge; it
  must not mutate authoritative state directly.
- Keep GPL/reference material reference-only unless a separate accepted ADR
  proves license, ownership, asset, notice, and relicense consequences.
- Preserve the public snapshot and all historical refs. Do not fabricate
  licensed-host, launch, artifact, provenance, or AgilePlus evidence.
- Do not push, merge, or enable auto-merge without a protected-flow decision,
  required checks, and recorded reviewer state.
- The organization-wide review-bot reconciliation loop (review findings ->
  isolated fix -> CI/review rerun) is a control-plane concern. Civic provides
  evidence and gate contracts to that loop; it does not silently implement or
  authorize the loop here.

## Ownership and Handoff

The program coordinator owns the acceptance decision and cross-lane sequencing.
Each WP lane owns its implementation, tests, contracts, evidence, and review
response. A handoff is valid only when it contains all of the following:

```text
feature slug + WP ID
owner + lane status + named blocker (if blocked)
base ref and subject commit
changed paths and ownership boundary
FR/QR IDs and test IDs
exact commands, result, and output/artifact hash
security/license/privacy/localization/performance impact
reviewer and review state
PR/commit and Airlock or preservation reference
next gate, dependency, and acceptance timestamp
```

No worker may silently broaden a WP's file scope, overwrite another lane's
work, or treat a local check as hosted merge/release proof. A blocked item must
name an owner, evidence, and next review date. The coordinator reconciles
these fields against AgilePlus state before advancing a dependency.

## Work Package Gate

AgilePlus currently records `civic-warfare-program` as `planned` with all 20
WPs planned and none doing, review, done, or blocked. WP01 is the first gate:

| Required WP01 evidence                      | Current boundary                              |
| ------------------------------------------- | --------------------------------------------- |
| Public audit build and baseline tests       | Public lane documented and locally checkable  |
| Licensed adapter build and launch smoke     | Pending a legally configured Windows/CS2 host |
| Artifact hashes and provenance              | Pending the licensed-host evidence bundle     |
| AgilePlus evidence record                   | Pending a supported recording API/CLI path    |
| Independent review and conditional go/no-go | Pending all preceding evidence                |

WP02 and later WPs may research, design, test, and benchmark in isolation, but
their production implementation cannot be accepted before WP01. The reviewed
dependency DAG and per-WP scopes are in `.agileplus/civic-warfare-program/plan.md`
and `tasks.md`.

## Pull Requests and References

The current local program-docs branch is `chore/civic-program-docs`. The
following subject SHA is a dated evidence snapshot, not a self-maintaining
claim about the current checkout: `3821fac` (2026-08-27 intent-ledger
snapshot). The preserved program branch is
`feat/civic-warfare-program` at `3bd4431b083101669fc9244e2e09afe182c2b10b`.

Live PR evidence was observed at `2026-08-27T10:14:24Z` with:

```text
gh pr list --repo KooshaPari/CivicSurvival-public --state open \
  --json number,headRefOid,state,mergeStateStatus,reviewDecision,updatedAt,statusCheckRollup
```

| PR  | Head SHA                                   | Scope                               | Merge/review state                       | Current non-passing checks                                                                  |
| --- | ------------------------------------------ | ----------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| #2  | `3bd4431b083101669fc9244e2e09afe182c2b10b` | Preserved reviewed decomposition    | Open; dirty/conflicting; review required | Mergify Merge Queue, Summary; Socket alert neutral                                          |
| #3  | `a360684887e2702ea3c79d628d9ca5681cc13d9c` | Program specification/docs          | Open; blocked; changes requested         | Mergify Merge Queue, Summary                                                                |
| #4  | `be3b1c15c905da5f56fe4968da687046b1491d89` | Security/Mergify workflow hardening | Open; blocked; review required           | scorecard, Dependency Review, Mergify Merge Queue, Summary; Infisical queued                |
| #5  | `b7b7161dc27c47ff05b732db81927c4594514627` | Runnable public audit evidence lane | Open; blocked; review required           | scorecard, Dependency Review, Security Scan, Mergify Merge Queue, Summary; Infisical queued |

These PRs are separate evidence lanes. No review, merge, or release acceptance
is implied by a local branch, a passing local command, or a generated artifact.

### Mergify Bootstrap Blocker

At the same observation point, the PR #3 Mergify failures were traced to the
base branch, not to an unmet documentation check. `origin/main` at
`32518d2acf901a21a61caa16b13c93482ae4d6fc` still contains invalid Mergify
constructs including unsupported `post_merge`, combined bot-author conditions,
`github_accounts` under review requests, and `age>=30d`. PR #3 carries a
corrected `.mergify.yml`, but Mergify evaluates the base configuration before
the PR can refresh its Queue and Summary automation. This is a Mergify
bootstrap loop, not a branch-protection deadlock.

Resolution requires a protected-flow decision by the Civic coordinator or
repository administrator to admit PR #3's validated `.mergify.yml` correction
through the ordinary protected PR path, then confirm a fresh Queue and Summary
result. Current `main` protection requires the five CI checks, a fresh approval,
and resolved conversations; it does not require Mergify Queue or Summary.
This document does not authorize a workflow change, a bypass, or a merge.

### PR #3 Review-Resolution Gate

As of `2026-08-28T06:05Z`, PR #3 has 53 review threads: 39 resolved and 14
unresolved. Ten are current and four are outdated. The Mergify configuration
can only be bootstrapped after the current review surface is resolved or
explicitly dispositioned:

| Class                          | Current affected paths                                                                             | Required disposition                                                                                                |
| ------------------------------ | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| ABI contract already corrected | `.agileplus/civic-warfare-program/contracts/civic_warfare.h`, `contracts/public-api.md`            | Reply with the current `CommandDecision` versus `CswResult` contract and resolve the obsolete thread.               |
| Truncated work-package titles  | `.agileplus/civic-warfare-program/tasks/WP10*`, `tasks/WP14*`, `tasks/WP15*` through `tasks/WP20*` | Restore full matching YAML and heading titles.                                                                      |
| Dependency-delta policy        | `.github/workflows/ci.yml`                                                                         | Replace blanket manifest rejection with declared ecosystem support or a narrower policy.                            |
| Scorecard action hygiene       | `.github/workflows/scorecard-ci.yml`                                                               | Pin actions, disable persisted checkout credentials, and isolate any PR-comment token to its least-privileged step. |
| Quality-policy semantics       | Civic quality specification and governance text                                                    | Clarify workflow-scoped `needs`, PR versus protected-push behavior, and exact WP17/WP18/WP19 prerequisite rules.    |
| Already addressed evidence     | `.github/workflows/ci.yml`, tracked `Tools/`, `scripts/contract_check.py`                          | Reply with the current fail-closed security lines, paths, and green Civic Evidence Gate; resolve obsolete threads.  |

Four additional threads are outdated: the destroy ABI signature, an earlier
title batch, stale CI-probe wording, and a relocated ABI-remediation command.
They require current-line verification before resolution but do not establish a
new defect. No thread may be resolved by this chat without Chat C's review and
path/SHA handoff.

### Successor PR Decomposition

The following additional findings were observed on `2026-08-27` and are
preserved to prevent a future coordinator from treating all failed checks as
one Mergify symptom:

| PR                                               | Verified finding                                                                                                                                                                                                                                                                                                                              | Required owner decision                                                                                                                                          |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| #4 at `be3b1c15c905da5f56fe4968da687046b1491d89` | Its `.mergify.yml` requires a non-existent `Civic Evidence Gate`; Dependency Review fails because Dependency Graph is disabled; Scorecard reports `11/88 < 85`.                                                                                                                                                                               | Chat C must correct the unsatisfiable check condition, decide whether Dependency Graph is required, and assign the base Scorecard policy/repository remediation. |
| #5 at `b7b7161dc27c47ff05b732db81927c4594514627` | Security Scan/Gitleaks fails before scanning because the shallow checkout lacks comparison revision `857fdab3bfe0613545d11688087ad29f1673a15d`. Artifact `9633981837` is a partial scan only. A preceding base run also reports two pre-existing `generic-api-key` findings in `CivicSurvival/Localization/en-US.json` at lines 238 and 1112. | Chat C must provide full PR comparison history to Gitleaks, remediate or explicitly triage the base findings, and require a fresh non-partial scan.              |

PR #4's `ci / lint`, `ci / test`, and CI Security Scan pass. PR #5's
`ci / lint` and `ci / test` pass, but its CI Security Scan does not. None of
these observations authorizes a source/workflow modification from this chat.

The two base findings are ordinary localization strings: `en-US.json:238`
contains "Your offshore account just became {0}% less secret." and
`en-US.json:1112` contains "International monitors request access." They are
likely generic-token false positives, not credentials, but remain failed
security evidence until a security owner records the exact Gitleaks rule,
performs a full-history before/after scan, and justifies a narrowly scoped
exception without masking genuine secrets.

PR #5's immediate scan-infrastructure correction is known: add
`fetch-depth: 0` to the Security Scan checkout in `.github/workflows/ci.yml`.
The hardened local lineage already contains that exact remedy at `ced0063`; PR
The PR does not. A full-history local scan over 104 commits and 16.06 MB found only
the two localization matches above. Any future `.gitleaks.toml` must retain
the default rules and constrain an allowlist by both exact path and exact line
regex; it must not disable `generic-api-key` or ignore the entire file.

## Prompt Ledger

Every delegated task must be traceable to one feature/WP and one owner. The
following ledger is the minimum handoff record; an empty or invented field is a
blocked handoff, not a partial acceptance.

| Field           | Required value                                                             |
| --------------- | -------------------------------------------------------------------------- |
| Prompt identity | Stable task ID, date, and requesting coordinator                           |
| Scope           | Feature slug, WP, FR/QR IDs, allowed paths                                 |
| Ownership       | Named worker, reviewer, and decision owner                                 |
| Provenance      | Base ref, subject SHA, branch/worktree, preservation status                |
| Work result     | Changed paths, tests, exact commands, outputs and hashes                   |
| Risk            | Blockers plus security, license, privacy, localization, performance impact |
| Handoff         | PR/commit, review state, next dependency/gate, timestamp                   |

No prompt may authorize direct SQLite evidence fabrication, force-push, hidden
scope expansion, or bypass of a required reviewer or licensed-host gate.

### Populated Civic intent records

| Prompt ID     | Direct substantive user prompt (CP+Paste)                                                                                                                                                                                                                                                                        | Derived synthesis / answer                                                                                                                                 | Status                               | Agent session                                   |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------- |
| CIVIC-INT-001 | "For your repos in scope temporarily pause new work. we have many branches, checkouts, stashes, wtrees and potential novel work hidden in commit histories that you should review and recover/merge into main, get down to 1 branch without arbitrary delete or drops true semantic merge/review/approve churn." | Preserve-first reconciliation is required; Civic work stays in provenance/review gates until each candidate has evidence and protected integration.        | active; not complete                 | coordinator session; delegated Civic audit lane |
| CIVIC-INT-002 | "Mac is out of space; all new work must be subtractive oriented on this entire FS ... avoid work that requires new checkouts ... backed up correctly ... audit for proper long term grade cleanup."                                                                                                              | Treat local checkout, database, refs, and artifacts as protected until provenance and backup evidence exist; no opportunistic cleanup.                     | active; preservation gate            | coordinator session; estate audit lane          |
| CIVIC-INT-003 | "Regardless of a drop ... review cockpit in whole and update it ... work items seem weakly represented ... prompts must be explicit CP+Paste from my words, intent is this + your response/synthesis."                                                                                                           | Civic evidence work must expose human-readable outcomes, exact prompt provenance, agent ownership, tests, hashes, blockers, and human approval boundaries. | active; ledger schema populated here | coordinator session; Civic docs lane            |
| CIVIC-INT-004 | "For all repos in scope pause new work until all existing work in local AND remote stash, branches, dirties is PR'd -> review/optimality/polish churn -> CI green ... then back to new works."                                                                                                                   | Civic PRs remain gated; local pass results cannot substitute for hosted checks, review, or protected merge.                                                | blocked on hosted/review gates       | coordinator session; Civic PR lanes             |
| CIVIC-INT-005 | "go deeper/wider/refine the past/present/future aligned WBS/state ... backed by web/local/remote ... deep audits and researches."                                                                                                                                                                                | Maintain dated, machine-verifiable state snapshots and distinguish current evidence from historical claims.                                                | active; control-plane tracked        | coordinator session; control-ledger lane        |

### Verbatim Civic coordination directives

The following user directives are preserved verbatim because they establish the
active Civic ownership and pause-resilient delivery contract. Short `proc` and
other tick-only messages are intentionally excluded.

#### CIVIC-INT-006: exclusive program ownership

> We should run the two Civic managers as one program with strict ownership,
> not as two independent implementers.
>
> Chat C (this manager): Civic repo governance, preserved refs, PR
> decomposition, ABI/contracts, audit tooling, CI/Mergify, documentation,
> local verification, GitHub queue.
>
> Other Civic manager: Main-PC execution only: licensed Windows/CS2 build,
> runtime smoke tests, native toolchain validation, performance/runtime
> evidence, artifact capture.
>
> The second manager must not edit Civic source unless I explicitly hand off a
> named file/path and commit range. I must not duplicate its licensed-host/runtime
> work.

Derived rule: this repository accepts only coordinator-owned source, contract,
CI, documentation, and PR work. Main-PC evidence is read-only input until its
manifest is verified against the supplied subject SHA.

#### CIVIC-INT-007: required handoff envelope

> Every handoff should contain only: owner; repository/ref; exact commit SHA;
> allowed paths; command to run; expected artifact IDs; return channel;
> expiry/stop condition.

Derived rule: the expanded handoff table in this document is mandatory. Missing
or unverifiable fields keep the item blocked; they never imply acceptance.

#### CIVIC-INT-008: licensed-host boundary

> Prefer fetching from GitHub on the main PC rather than copying a dirty
> workspace. If network access is unavailable, use an immutable bundle ...
> Never transfer secrets, license tokens, or uncommitted build output. Only the
> resulting logs, hashes, and sanitized evidence bundle should come back.

Derived rule: local macOS work cannot substitute for a licensed Windows/CS2
adapter build, attach/handshake, launch smoke, runtime behavior, or performance
evidence. Those are WP01 external evidence gates.

#### CIVIC-INT-009: immutable scope and archive

> Scope remains exclusive to KooshaPari/CivicSurvival-public, upstream
> reference Theorist100/CivicSurvival-public, and archive ref
> origin/feat/civic-warfare-program @ 3bd4431b...
>
> Archive ref remains immutable. Do not modify, reset, force-push, delete,
> prune, or rewrite it.
>
> No OmniRoute or other Phenotype repository is in scope. Do not modify Civic
> files without an explicit path/SHA ownership handoff from Chat C.

Derived rule: this is the scope supersession record. It overrides earlier
cross-repository coordination notes for this Civic handoff.

#### CIVIC-INT-010: pause-resilient documentation request

> going to pause you on this device, write docs/intent and commit to civic
> survival, see how we've done that subfolder before, includes intent.md which
> is MY EXPLICIT PROMPTS AND QUESTION ANSWERS IN DEPTH WHERE NOT PROC OR OTHER
> MEANINGLESS TICK PLUS YOUR DERIVED SYNTHESIS AND EXPANSION AROUND IT, ON TOP
> OF FULL AGILEPLUS SPECS AND ALL ADRS AND OTHER EXPECTED DOCS SPECS AND
> GOVERNANCE PLUS TESTS AND TEST/QUALITY INFRA.

Derived rule: `docs/intent.md`, `docs/intent-traceability.md`, ADR-0001, and
the checked-in AgilePlus artifacts form the durable local handoff. This is not
a claim that the untracked runtime database or licensed-host evidence has been
reproduced.

## PR, Requirement, and QA Mapping

| Delivery lane               | Governing requirements                                 | Required QA/evidence                                                   |
| --------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------- |
| PR #3 program specification | `FR-001..FR-120`, `QR-001..QR-020`, WP01-WP20 planning | traceability, DAG acyclicity, governance JSON, docs review             |
| PR #5 public audit          | `FR-001..FR-005`, `FR-101`                             | public C# audit/build, baseline tests, strict Civic Evidence Gate      |
| PR #4 security/CI           | `FR-004..FR-005`, `QR-*` affected by CI/security       | workflow lint, Security Scan, Dependency Delta, privacy/license review |
| Future WP02 successor       | `FR-006..FR-010`, `FR-102`                             | pinned Rust/FlatBuffers, ABI contract, C smoke, architecture tests     |

The QA command contract is defined by `.github/civic-quality-policy.json` and
`.github/workflows/ci.yml`; every FR evidence record must retain its test ID,
command/output hash, review reference, and acceptance time.

The complete authoritative requirement-to-WP contract is indexed in
`docs/intent-traceability.md`. That index deliberately points to, rather than
duplicates or reinterprets, the checked-in AgilePlus specification and task
contracts.

## Verification Contract

The versioned policy is `.github/civic-quality-policy.json`; its strict
evaluator is `scripts/civic_quality_gate.py`. The required public checks are:

```text
python3 -m pytest -q
python3 scripts/contract_check.py
node Tools/generate-binding-manifest.js --check
node Tools/sync-binding-codegen.js --check
python3 scripts/civic_quality_gate.py --policy .github/civic-quality-policy.json --strict .
```

The corresponding test coverage is in
`tests/test_civic_quality_gate.py`, `tests/test_civic_abi_contract.py`,
`tests/test_wp01_evidence.py`, and `tests/test_binding_projections.py`.
The CI wiring and required job dependencies are in `.github/workflows/ci.yml`.

The checked-in WP01 manifest template is intentionally
`CONDITIONAL_NO_GO`: `python3 scripts/verify_wp01_evidence.py REPO MANIFEST`
fails closed until every required record, subject commit, artifact hash,
licensed-host fact, and supported AgilePlus evidence record is present.
`flatc` and the historical native/WP02 trees are intentionally deferred to a
future pinned-toolchain successor lane.

### Current locally verified outcomes

Observed on `2026-08-27` from the Civic program-docs branch:

| Command                                                                                                                                                | Result                                                                  | Evidence boundary                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- | ---------------------------------------------- |
| `git diff --check 3821fac^ 3821fac`                                                                                                                    | pass                                                                    | intent document introduction                   |
| `git diff --check 9b0db159^ 9b0db159`                                                                                                                  | pass                                                                    | ADR and traceability update                    |
| `git diff --check`                                                                                                                                     | pass on the staged documentation tree committed as the current revision | current documentation syntax/whitespace        |
| `python3 -m pytest -q tests/test_civic_quality_gate.py tests/test_civic_abi_contract.py tests/test_wp01_evidence.py tests/test_binding_projections.py` | 21 passed                                                               | public policy, ABI, WP01 fail-closed, bindings |
| `python3 scripts/contract_check.py`                                                                                                                    | pass; 1,114 C# binding values represented in generated TypeScript       | public binding projection only                 |

These results do not establish hosted CI success, reviewer approval, merge
readiness, licensed-host execution, or WP01 acceptance.

## Canonical Paths

- Feature specification and requirements: `.agileplus/civic-warfare-program/spec.md`
- Reviewed plan and dependencies: `.agileplus/civic-warfare-program/plan.md`
- WP registry and evidence contract: `.agileplus/civic-warfare-program/tasks.md`
- Program governance: `.agileplus/civic-warfare-program/contracts/governance-program.md`
- Machine policy: `.agileplus/civic-warfare-program/contracts/governance-v1.json`
- WP01 decision: `.agileplus/civic-warfare-program/wp01-go-no-go.md`
- Quality policy/design: `.github/civic-quality-policy.json` and `docs/superpowers/specs/2026-08-25-civic-quality-gate-design.md`
