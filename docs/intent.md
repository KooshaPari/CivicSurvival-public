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

| Required WP01 evidence | Current boundary |
| --- | --- |
| Public audit build and baseline tests | Public lane documented and locally checkable |
| Licensed adapter build and launch smoke | Pending a legally configured Windows/CS2 host |
| Artifact hashes and provenance | Pending the licensed-host evidence bundle |
| AgilePlus evidence record | Pending a supported recording API/CLI path |
| Independent review and conditional go/no-go | Pending all preceding evidence |

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

| PR | Scope | Current review boundary |
| --- | --- | --- |
| #2 | Preserved reviewed decomposition | Open; dirty/conflicting; review required |
| #3 | Program specification/docs | Open; changes requested |
| #4 | Security/Mergify workflow hardening | Open; review required |
| #5 | Runnable public audit evidence lane | Open; review required |

These PRs are separate evidence lanes. No review, merge, or release acceptance
is implied by a local branch, a passing local command, or a generated artifact.

## Prompt Ledger

Every delegated task must be traceable to one feature/WP and one owner. The
following ledger is the minimum handoff record; an empty or invented field is a
blocked handoff, not a partial acceptance.

| Field | Required value |
| --- | --- |
| Prompt identity | Stable task ID, date, and requesting coordinator |
| Scope | Feature slug, WP, FR/QR IDs, allowed paths |
| Ownership | Named worker, reviewer, and decision owner |
| Provenance | Base ref, subject SHA, branch/worktree, preservation status |
| Work result | Changed paths, tests, exact commands, outputs and hashes |
| Risk | Blockers plus security, license, privacy, localization, performance impact |
| Handoff | PR/commit, review state, next dependency/gate, timestamp |

No prompt may authorize direct SQLite evidence fabrication, force-push, hidden
scope expansion, or bypass of a required reviewer or licensed-host gate.

### Populated Civic intent records

| Prompt ID | Direct substantive user prompt (CP+Paste) | Derived synthesis / answer | Status | Agent session |
|---|---|---|---|---|
| CIVIC-INT-001 | "For your repos in scope temporarily pause new work. we have many branches, checkouts, stashes, wtrees and potential novel work hidden in commit histories that you should review and recover/merge into main, get down to 1 branch without arbitrary delete or drops true semantic merge/review/approve churn." | Preserve-first reconciliation is required; Civic work stays in provenance/review gates until each candidate has evidence and protected integration. | active; not complete | coordinator session; delegated Civic audit lane |
| CIVIC-INT-002 | "Mac is out of space; all new work must be subtractive oriented on this entire FS ... avoid work that requires new checkouts ... backed up correctly ... audit for proper long term grade cleanup." | Treat local checkout, database, refs, and artifacts as protected until provenance and backup evidence exist; no opportunistic cleanup. | active; preservation gate | coordinator session; estate audit lane |
| CIVIC-INT-003 | "Regardless of a drop ... review cockpit in whole and update it ... work items seem weakly represented ... prompts must be explicit CP+Paste from my words, intent is this + your response/synthesis." | Civic evidence work must expose human-readable outcomes, exact prompt provenance, agent ownership, tests, hashes, blockers, and human approval boundaries. | active; ledger schema populated here | coordinator session; Civic docs lane |
| CIVIC-INT-004 | "For all repos in scope pause new work until all existing work in local AND remote stash, branches, dirties is PR'd -> review/optimality/polish churn -> CI green ... then back to new works." | Civic PRs remain gated; local pass results cannot substitute for hosted checks, review, or protected merge. | blocked on hosted/review gates | coordinator session; Civic PR lanes |
| CIVIC-INT-005 | "go deeper/wider/refine the past/present/future aligned WBS/state ... backed by web/local/remote ... deep audits and researches." | Maintain dated, machine-verifiable state snapshots and distinguish current evidence from historical claims. | active; control-plane tracked | coordinator session; control-ledger lane |

Records above preserve the user's substantive wording in abbreviated direct
form and identify the corresponding synthesis, status, and delegated session.
The complete organization-level prompt ledger remains in the control-plane WBS;
this file records only Civic-relevant entries.

## PR, Requirement, and QA Mapping

| Delivery lane | Governing requirements | Required QA/evidence |
| --- | --- | --- |
| PR #3 program specification | `FR-001..FR-120`, `QR-001..QR-020`, WP01-WP20 planning | traceability, DAG acyclicity, governance JSON, docs review |
| PR #5 public audit | `FR-001..FR-005`, `FR-101` | public C# audit/build, baseline tests, strict Civic Evidence Gate |
| PR #4 security/CI | `FR-004..FR-005`, `QR-*` affected by CI/security | workflow lint, Security Scan, Dependency Delta, privacy/license review |
| Future WP02 successor | `FR-006..FR-010`, `FR-102` | pinned Rust/FlatBuffers, ABI contract, C smoke, architecture tests |

The QA command contract is defined by `.github/civic-quality-policy.json` and
`.github/workflows/ci.yml`; every FR evidence record must retain its test ID,
command/output hash, review reference, and acceptance time.

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

## Canonical Paths

- Feature specification and requirements: `.agileplus/civic-warfare-program/spec.md`
- Reviewed plan and dependencies: `.agileplus/civic-warfare-program/plan.md`
- WP registry and evidence contract: `.agileplus/civic-warfare-program/tasks.md`
- Program governance: `.agileplus/civic-warfare-program/contracts/governance-program.md`
- Machine policy: `.agileplus/civic-warfare-program/contracts/governance-v1.json`
- WP01 decision: `.agileplus/civic-warfare-program/wp01-go-no-go.md`
- Quality policy/design: `.github/civic-quality-policy.json` and `docs/superpowers/specs/2026-08-25-civic-quality-gate-design.md`
