# Civic Evidence Quality Gate Design

## Decision

The generic 88-pillar scan remains available as a non-blocking inventory report. It
does not determine mergeability because it rewards unrelated platform claims such as
Kubernetes, WAF, VPN, and CDN configuration that are not part of this public Cities:
Skylines II client.

Mergeability instead requires a Civic-specific evidence gate. Every required rule is
grounded in a checked-in Civic artifact or a command that can run in public CI. A
licensed CS2 native launch is deliberately not represented as a public-CI pass; it is
reported as the separately owned WP01 evidence gate.

## Scope and non-goals

This change creates the policy, evaluator, tests, report, and GitHub Action wiring.
It does not implement gameplay, claim a public full build, introduce a server, or
reclassify a missing licensed-host proof as passing.

The evaluator owns only repository evidence. It does not execute the CS2 mod, inspect
private source generators, or infer that a document proves runtime correctness.

## Required rules

The policy version is `1`. Passing requires every rule below. Each rule carries a
stable identifier, a rationale, and an explicit probe so reports are actionable.

| ID | Evidence | Probe |
|---|---|---|
| `CIVIC-DOC-001` | Public-audit entrypoints | Root `README.md`, `BUILDING.md`, `USER_GUIDE.md`, `PRIVACY.md`, `NOTICE.md`, `CONTRIBUTING.md`, and `LICENSE` exist. |
| `CIVIC-DOC-002` | Honest build boundary | `README.md` contains the public-snapshot limitation and links to `BUILDING.md`; `BUILDING.md` exists. |
| `CIVIC-CONTRACT-001` | Public contract surface | `CivicSurvival.sln` and `CivicSurvival.Contracts/CivicSurvival.Contracts.csproj` exist. The installed-game build is reported as `host-required`, not passed, unless a licensed host supplies its evidence. |
| `CIVIC-UI-001` | UI contract integrity | `npm run check:contracts` runs from `CivicSurvival/UI`. |
| `CIVIC-UI-002` | UI static integrity | `npm run typecheck:declarations`, `npm run test:lint-rules`, and `npm run lint:strict` run from `CivicSurvival/UI`. |
| `CIVIC-UI-003` | UI behavioral integrity | `npm run test:ui` runs from `CivicSurvival/UI`. |
| `CIVIC-UI-004` | UI bundle budget | `bundle-baseline.json` exists and `npm run bundle:check` runs from `CivicSurvival/UI`. |
| `CIVIC-SEC-001` | Secret scan | The existing `ci / Security Scan` job completes successfully. This is consumed through the required-check aggregation, not duplicated by the evaluator. |
| `CIVIC-SEC-002` | Dependency-change scrutiny | The existing `ci / Dependency Delta` job completes successfully. This prevents silent dependency-manifest changes until a real ecosystem scanner is introduced. |
| `CIVIC-PROGRAM-001` | Warfare program traceability | `.agileplus/civic-warfare-program/spec.md`, `plan.md`, `tasks.md`, and `contracts/governance-v1.json` exist; the evaluator requires 120 unique `FR-001` through `FR-120`, 20 unique `QR-001` through `QR-020`, and 20 WP task files. |
| `CIVIC-PROGRAM-002` | Reviewed DAG and licensed-host boundary | The evaluator validates governance JSON, checks the declared WP graph is acyclic, and reports WP01 as `external_gate: pending` until a licensed host produces build, launch-smoke, artifact-hash, and provenance evidence. It never turns that pending state into a public-CI pass. |
| `CIVIC-CI-001` | Gate integrity | The Civic workflow invokes the evaluator with `--strict`; its job fails on a missing required rule. |

`CIVIC-UI-001` through `CIVIC-UI-004` are command checks and run only after a locked
`npm ci` in the UI directory. `CIVIC-SEC-001` and `CIVIC-SEC-002` are workflow-job
dependencies rather than file checks. The Civic gate is therefore a job in the
existing `.github/workflows/ci.yml`, configured with `needs: [security, dep-review]`
and an explicit fail-closed dependency-result check. This retains the actual checks
already validated on PR #3 without duplicating scanners or pretending the evaluator
can reproduce them. A separate workflow would not be valid because GitHub Actions
does not allow `needs` across workflow files.

## Data contract

`civic-quality-policy.json` is the versioned source of truth. It has a `version`, a
`required_rule_ids` array, and rule records with `id`, `kind`, `path` or `paths`, and
`description`. The evaluator rejects unknown rule kinds, duplicate IDs, required IDs
that are not declared, and policies with no required rules.

`scripts/civic_quality_gate.py <repo> --policy <path> --output json --strict` writes:

```json
{
  "policy_version": 1,
  "required_passed": true,
  "passed_rule_ids": ["CIVIC-DOC-001"],
  "failed_rules": [],
  "external_gates": [{"id": "WP01", "state": "pending"}]
}
```

The command exits `0` only when every required repository rule passes. It exits `1`
for an evidence failure and `2` for an invalid policy or invocation. `external_gates`
are informational and cannot change that exit code.

## CI behavior

`.github/workflows/ci.yml` gains a `Civic Evidence Gate` job on pull requests and
protected-branch pushes. It runs after `security` and `dep-review`, performs the
locked UI command checks, invokes the evaluator, publishes the JSON and Markdown
report as an artifact, and exposes one required check named `Civic Evidence Gate`.

The legacy 88-pillar workflow changes to report-only: it still uploads its inventory
and comments its score, but the target failure is an annotation rather than a failed
job. It must keep the 85 target in the report so trend evidence is not erased. The
branch rule is updated outside this repository to require `Civic Evidence Gate`,
`ci / lint`, `ci / test`, `Security Scan`, and `Dependency Delta`.

## Verification

Python unit tests cover each rule kind, missing evidence, malformed policies,
strict-mode exit codes, and the fact that WP01 pending does not become a public-CI
pass. Workflow linting uses `actionlint`; the evaluator is run against the repository
in strict mode. Hosted verification confirms that the Civic gate, security scan,
dependency delta, lint, and test checks run on the exact PR head SHA.

## Future evolution

New rules require a policy-version bump, a test, an artifact-backed rationale, and a
separate reviewable PR. A licensed native smoke result may become a release gate only
when its evidence is produced on a legally configured host; it must not be simulated
in public CI.
