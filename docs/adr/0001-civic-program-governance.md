# ADR-0001: Civic Program Governance and WP01 Boundary

- Status: Accepted for planning and evidence governance
- Date: 2026-08-27
- Decision owner: program coordinator
- Scope: `civic-warfare-program`, WP01-WP20

## Context

The public repository contains a large warfare and city-survival specification,
but does not contain the legally local Cities: Skylines II build environment.
AgilePlus records the feature as `planned` with 20 planned work packages. A
passing public document or contract check cannot establish installed-game
build, launch, artifact provenance, or runtime correctness.

## Decision

Keep the program in the `planned` state and keep the production warfare gate
closed until WP01 supplies all required public and licensed-host evidence.
Use `.agileplus/civic-warfare-program/` as the feature artifact root,
`.github/civic-quality-policy.json` as the public QA policy, and
`contracts/governance-program.md` as the acceptance contract. Require every
handoff to include owner, scope, exact subject SHA, commands/results, hashes,
review state, and next gate as recorded in `docs/intent.md`.

## Required WP01 Evidence

1. Public audit build and baseline tests.
2. Licensed Windows/CS2 adapter build and launch smoke.
3. Artifact hashes and provenance for that licensed host.
4. A supported AgilePlus evidence record for the feature/WP.
5. Independent specification/code review and a conditional go/no-go decision.

The checked-in `wp01-evidence.template.json` remains `CONDITIONAL_NO_GO` until
these records are real, subject-commit-bound, and hash-verified. Evidence may
not be inserted by direct database mutation.

## Consequences

- WP02-WP20 may conduct isolated research, design, tests, schemas, and
  benchmarks, but production warfare behavior cannot merge before WP01.
- ABI, schema, save, RNG, license, or new-language decisions require their
  own contract/version/provenance evidence and, where applicable, a follow-up
  ADR.
- Public CI can prove repository evidence only; it cannot turn the licensed
  host gate into a public-CI pass.
- A future ADR is required before importing copyleft implementation material or
  adding a language outside the locked Rust/C#/TypeScript stack.

## Verification References

- `.agileplus/civic-warfare-program/wp01-go-no-go.md`
- `.agileplus/civic-warfare-program/wp01-licensed-evidence-runbook.md`
- `.agileplus/civic-warfare-program/contracts/governance-program.md`
- `docs/superpowers/specs/2026-08-25-civic-quality-gate-design.md`
- `docs/sessions/20260722-civic-warfare-program/06_TESTING_STRATEGY.md`
