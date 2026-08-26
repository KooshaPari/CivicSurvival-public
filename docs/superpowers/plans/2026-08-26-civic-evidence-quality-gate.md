# Civic Evidence Quality Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Each task is test-first and ends with a focused verification command.

**Goal:** Replace the generic 88-pillar merge blocker on Civic PRs with a versioned, evidence-backed Civic quality gate, while retaining the generic scorecard as report-only trend evidence.

**Architecture:** A small, dependency-free Python evaluator reads a checked-in policy and emits deterministic JSON/Markdown evidence. The existing `.github/workflows/ci.yml` gains one strict `Civic Evidence Gate` job after the existing security and dependency-delta jobs; a separate workflow is deliberately not used because GitHub Actions cannot express `needs` across workflow files. UI commands run as explicit CI steps after a locked install. The licensed CS2/native launch remains an external WP01 gate and is reported as pending, never simulated as public-CI success.

**Tech Stack:** Python 3.11 standard library, JSON, GitHub Actions YAML, Node/npm scripts already present in `CivicSurvival/UI`, `actionlint`.

---

## Scope and invariants

- Do not implement warfare gameplay, economy mechanics, or native runtime behavior in this PR.
- Do not lower the generic scorecard threshold or fabricate generic pillar passes.
- Do not run a licensed CS2 build in public CI.
- Do not mutate or delete the preserved `feat/civic-warfare-program` branch or its archive PR.
- Every required Civic rule has a stable ID, a checked-in probe, and a testable failure mode.
- `external_gates` are informational and cannot make a failed public rule pass.
- A malformed policy exits `2`; an evidence failure exits `1`; a complete pass exits `0`.
- The gate must fail closed when `security` or `dep-review` is not successful.

## File map

Create:

- `.github/civic-quality-policy.json` — versioned rule manifest.
- `scripts/civic_quality_gate.py` — evaluator and JSON/Markdown reporter.
- `tests/test_civic_quality_gate.py` — unit tests and temporary-repository fixtures.

Modify:

- `.github/workflows/ci.yml` — strict Civic job, UI commands, report artifact, and dependency-result guard.
- `.github/workflows/scorecard-ci.yml` — retain the audit/report/comment but remove target failure as a merge blocker.

Document/verify:

- `docs/superpowers/specs/2026-08-25-civic-quality-gate-design.md` — already records the corrected same-workflow architecture; update only if implementation details materially change the contract.
- `docs/superpowers/plans/2026-08-26-civic-evidence-quality-gate.md` — this plan; check off tasks as completed.

## Task 1: Establish failing evaluator tests

**Files:** create `tests/test_civic_quality_gate.py`.

Write tests before implementation. Use `tempfile.TemporaryDirectory` to construct small repositories and invoke the evaluator through its importable functions and subprocess CLI. Tests must cover:

1. A complete fixture returns exit `0`, `required_passed: true`, all required IDs passed, and `WP01` appears under `external_gates` with state `pending`.
2. Missing one required documentation path returns exit `1` and identifies exactly `CIVIC-DOC-001`.
3. README build-boundary text missing or missing `BUILDING.md` returns `CIVIC-DOC-002`.
4. Missing solution/project contract returns `CIVIC-CONTRACT-001`.
5. Program traceability rejects missing or duplicate FR/QR IDs and fewer than 20 WP task files.
6. Program DAG parsing expands ranges such as `WP09-WP12`, finds a cycle in a fixture, and passes the real registry.
7. Governance JSON with invalid JSON or missing required transition rules fails `CIVIC-PROGRAM-002`.
8. A policy with duplicate IDs, unknown `kind`, absent required IDs, or no required rules exits `2`.
9. `--output json` is parseable and `--output markdown` contains a stable summary table.
10. `--strict` fails on required evidence but does not fail solely because WP01 is pending.

Run:

```bash
python -m pytest -q tests/test_civic_quality_gate.py
```

Expected first result: collection/import failure or red tests because the evaluator does not yet exist.

Commit: `test(civic): specify evidence gate behavior`.

## Task 2: Implement the policy loader and deterministic evaluator

**Files:** create `scripts/civic_quality_gate.py`.

Implement only Python standard-library code with these pieces:

1. `load_policy(path)` validates object shape, integer `version`, non-empty `required_rule_ids`, unique rule IDs, known rule kinds, and exact required-ID coverage. Resolve all repository paths relative to the repository argument and reject path traversal outside it.
2. Rule kinds:
   - `all_paths_exist`: verify every listed path is a regular file.
   - `text_contains`: verify a file contains every required literal substring.
   - `workflow_steps`: verify the expected workflow contains each exact command/name token; runtime execution remains the CI step’s responsibility.
   - `program_traceability`: extract exact `FR-001`..`FR-120` and `QR-001`..`QR-020` IDs from the declared artifacts, require no duplicates, and require exactly 20 task files whose front matter has unique `work_package_id` values `WP01`..`WP20`.
   - `program_dag`: parse the `Work Package Registry` table in `plan.md`, read the entry-dependency column, expand `WPnn-WPmm` ranges, reject unknown nodes, and run Kahn’s algorithm. Require all 20 nodes and no cycle. Validate `governance-v1.json` contains the two expected transition rules for each WP. Validate the WP01 go/no-go file contains a conditional no-go/licensed-host boundary; emit `WP01` as `{state: "pending", external: true}`.
3. Produce a stable report with `policy_version`, `required_passed`, `passed_rule_ids`, `failed_rules` containing `id`, `kind`, `reason`, and `external_gates`. Sort IDs and failures for deterministic diffs.
4. Implement CLI arguments `<repo> --policy PATH --output {json,markdown} [--strict]`; write to stdout only, use exit codes `0/1/2` above, and never treat external-gate pending as a failure.
5. Keep evaluator errors actionable: identify path, rule ID, and expected condition without dumping secrets or arbitrary file contents.

Run the focused test suite and a real-repository check:

```bash
python -m pytest -q tests/test_civic_quality_gate.py
python scripts/civic_quality_gate.py . --policy .github/civic-quality-policy.json --output json --strict
```

Commit: `feat(civic): add deterministic evidence evaluator`.

## Task 3: Add the checked-in policy

**Files:** create `.github/civic-quality-policy.json`.

Declare policy version `1`, all required IDs from the design, and explicit probes:

- `CIVIC-DOC-001`: the seven public-audit files.
- `CIVIC-DOC-002`: README literals proving public-snapshot/build boundary and `BUILDING.md` link, plus the file itself.
- `CIVIC-CONTRACT-001`: `CivicSurvival.sln` and `CivicSurvival.Contracts/CivicSurvival.Contracts.csproj`.
- `CIVIC-UI-001`..`004`: `.github/workflows/ci.yml` workflow-step tokens for `npm run check:contracts`, declaration typecheck/lint-rule/UI tests/strict lint, and bundle baseline/check; the actual commands are executed by the gate job.
- `CIVIC-SEC-001` and `CIVIC-SEC-002`: workflow dependency declarations for the existing `security` and `dep-review` jobs.
- `CIVIC-PROGRAM-001`: `spec.md`, `plan.md`, `tasks.md`, `contracts/governance-v1.json`, and the task glob.
- `CIVIC-PROGRAM-002`: `plan.md`, governance JSON, and `wp01-go-no-go.md`.
- `CIVIC-CI-001`: `.github/workflows/ci.yml` contains the evaluator invocation with `--strict` and the named gate job.

Do not encode a target score, native-host pass, or a mutable baseline in this policy.

Run:

```bash
python scripts/civic_quality_gate.py . --policy .github/civic-quality-policy.json --output markdown --strict
```

Commit: `chore(civic): define versioned evidence policy`.

## Task 4: Wire the strict Civic gate into the existing CI workflow

**Files:** modify `.github/workflows/ci.yml`.

Add a job named `civic-quality` with display name `Civic Evidence Gate` and `if: always()`. It must `needs: [security, dep-review]`, then fail immediately unless both dependency results are exactly `success`. This preserves fail-closed behavior even when upstream jobs are skipped, cancelled, or made advisory.

The job must:

1. Check out with full history only if required by an existing command; otherwise use the minimum safe checkout.
2. Set up Python 3.11 and Node 20.
3. Run `npm ci --ignore-scripts` or the repository-approved locked install in `CivicSurvival/UI`, then run the contract checks and the exact UI commands represented by `CIVIC-UI-001`..`004`: `check:contracts`, `typecheck:declarations`, `test:lint-rules`, `test:ui`, `lint:strict`, and `bundle:check`.
4. Run the evaluator with `--strict` and save both JSON and Markdown reports.
5. Upload reports as a uniquely named artifact on success or failure.
6. Avoid `continue-on-error` in this job. The job conclusion is the required Civic check.

Add a workflow-level static test in `tests/test_civic_quality_gate.py` that confirms the job name, `needs`, `if: always()`, strict invocation, and all required UI command tokens. Do not attempt to execute GitHub expressions locally.

Run:

```bash
python -m pytest -q tests/test_civic_quality_gate.py
actionlint .github/workflows/ci.yml
```

Commit: `ci(civic): enforce evidence gate after security checks`.

## Task 5: Convert the generic scorecard to report-only

**Files:** modify `.github/workflows/scorecard-ci.yml`.

Keep checkout, baseline provenance validation, the hard-coded minimum threshold of 85, JSON report generation, PR comment, and artifact upload. Change only mergeability behavior:

- invoke `scripts/scorecard_ci.py` without `--fail-on-drop` for the informational workflow path;
- keep target/regression values in the report and summary;
- make the status step print `INFORMATIONAL` when target or regression is not green and exit successfully;
- remove the final `Check score regression` failure step;
- preserve failure for malformed/missing audit output or invalid baseline configuration.

Add/update a test or static assertion ensuring the workflow no longer contains an active target-failure step while retaining the 85 threshold and baseline checks. The required branch rule will later be changed externally to require `Civic Evidence Gate`, not the generic scorecard.

Run:

```bash
python -m pytest -q tests/test_scorecard_ci.py tests/test_civic_quality_gate.py
actionlint .github/workflows/scorecard-ci.yml
```

Commit: `ci(scorecard): make generic inventory informational`.

## Task 6: Full local verification and evidence artifact

Run, in this order, from the repository root:

```bash
python -m pytest -q tests/test_scorecard_ci.py tests/test_civic_quality_gate.py
python scripts/civic_quality_gate.py . --policy .github/civic-quality-policy.json --output json --strict > civic-quality-report.json
actionlint .github/workflows/ci.yml .github/workflows/scorecard-ci.yml
(cd CivicSurvival/UI && npm ci)
(cd CivicSurvival/UI && npm run check:contracts)
(cd CivicSurvival/UI && npm run typecheck:declarations)
(cd CivicSurvival/UI && npm run test:lint-rules)
(cd CivicSurvival/UI && npm run test:ui)
(cd CivicSurvival/UI && npm run lint:strict)
(cd CivicSurvival/UI && npm run bundle:check)
```

Inspect the JSON for `required_passed: true`, all required rule IDs, and `WP01` pending. Do not claim the native host gate passed. Remove the generated root report if it is not intended as a committed artifact; the CI artifact is the durable report.

Commit: `test(civic): verify strict evidence gate locally` only if a tracked test/fixture change is required; otherwise leave no verification debris.

## Task 7: Review, hosted verification, and branch-protection handoff

Before opening/updating the successor PR:

1. Inspect `git diff --check`, `git status --short`, and the complete diff.
2. Verify no preserved branch, archive, or unrelated repository was modified.
3. Run an independent review focused on policy bypasses, path traversal, command injection, YAML expression correctness, and false-positive evidence.
4. Push the focused branch and verify checks on the exact PR head SHA.
5. Require green `Civic Evidence Gate`, `ci / lint`, `ci / test`, `Security Scan`, and `Dependency Delta`; keep the generic scorecard informational.
6. Update GitHub branch protection externally to require the Civic check. Do not admin-bypass protection or merge while required checks are pending.
7. Record the PR, commit SHA, test outputs, report artifact, review result, and remaining external WP01 blockers in the program evidence dossier.

Closure for this slice is reached only when the PR is reviewed, hosted checks are green, and branch protection points at the Civic gate. The overall warfare program remains open until licensed-host WP01 evidence and WPs 02-20 are separately accepted.

## Progress tracking

Mark each checkbox in this file only after the corresponding commit and verification command succeed:

- [x] Task 1 — failing evaluator tests
- [x] Task 2 — evaluator implementation
- [x] Task 3 — policy manifest
- [x] Task 4 — strict CI job (local evaluator/UI wiring verified; missing public helper tools remain a gate blocker)
- [x] Task 5 — report-only scorecard
- [x] Task 6 — local verification and exact-head hosted evidence gate (Civic gate, security, dependency, lint/test, scorecard, Semgrep, and Socket green at `f6b8848`; licensed WP01 remains pending)
- [ ] Task 7 — hosted review and branch-protection handoff (branch protection now requires Civic Gate, security, dependency, lint, and test; repository-controlled checks and latest Kilo pass; one human approval remains required before merge)
