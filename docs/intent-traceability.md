# Civic Intent Traceability Index

## Purpose

This index makes the Civic pause handoff navigable without duplicating the
authoritative AgilePlus requirements. The checked-in specification and task
contracts remain the source of truth; this document records where a future
agent must look and what evidence must return before a work package can move.

## Authority Order

1. `docs/intent.md`: explicit coordinator directives, ownership, live PR
   snapshot, and verified local outcomes.
2. `docs/adr/0001-civic-program-governance.md`: accepted planning and WP01
   boundary decision.
3. `.agileplus/civic-warfare-program/spec.md`: `FR-001..FR-120` and
   `QR-001..QR-020` definitions.
4. `.agileplus/civic-warfare-program/tasks.md` and `tasks/WP*.md`: WP scope,
   dependency order, and per-FR evidence record contract.
5. `.agileplus/civic-warfare-program/contracts/governance-program.md` and
   `contracts/governance-v1.json`: allowed state transitions and evidence
   semantics.
6. `.github/civic-quality-policy.json` and `.github/workflows/ci.yml`:
   repository quality rules and hosted gates.

## Work Package Cross-Reference

| WP | Authoritative requirement/evidence location | Dependency boundary | Acceptance evidence class |
| --- | --- | --- | --- |
| WP01 | `tasks/WP01*`, `wp01-evidence.template.json`, `wp01-go-no-go.md` | Entry gate | public audit, licensed host, hashes, AgilePlus record, review |
| WP02 | `tasks/WP02*`, ABI and FlatBuffers contracts | WP01 | ABI/codegen/contracts |
| WP03 | `tasks/WP03*` | WP02 | deterministic replay and golden vectors |
| WP04 | `tasks/WP04*` | WP03 | conservation and equivalence tests |
| WP05-WP08 | `tasks/WP05*` through `tasks/WP08*` | DAG in `tasks.md` | domain/property/balance tests |
| WP09-WP12 | `tasks/WP09*` through `tasks/WP12*` | WP04/WP07/WP08 branches | scenario and capability tests |
| WP13-WP16 | `tasks/WP13*` through `tasks/WP16*` | upstream domain branches | lifecycle, uncertainty, fairness tests |
| WP17-WP18 | `tasks/WP17*`, `tasks/WP18*` | integration branches | UI journey, accessibility, localization, content validation |
| WP19 | `tasks/WP19*` | starts WP02; exits all | test matrix, budgets, fuzz/failure, evidence export |
| WP20 | `tasks/WP20*` | WP01-WP19 | provenance, packaging, release dossier |

For every `FR-001..FR-120` and `QR-001..QR-020`, the mandatory record is:

```text
FR/QR ID -> WP -> implementation paths -> test IDs -> command/output hash
-> benchmark/security/license evidence -> review -> commit/PR
-> acceptance timestamp
```

The full FR/QR text is intentionally not copied here. It is authoritative in
`spec.md`; generated duplication would create a second, stale requirements
source.

## WP01 Required Artifact IDs

```text
WP01:public_audit_build
WP01:baseline_tests
WP01:licensed_adapter_build
WP01:launch_smoke
WP01:artifact_hash_provenance
WP01:agileplus_evidence_record
WP01:conditional_go_no_go_pass
```

The first two can be gathered locally. The licensed adapter, launch smoke, and
runtime/performance evidence belong exclusively to the named main-PC manager
and must return as sanitized hashes/logs/manifest data bound to the exact
Git subject SHA. No secrets, license tokens, uncommitted build output, or
unverified database edits are valid evidence.

## Verification Matrix

| Concern | Public command/source | What it proves | What remains external |
| --- | --- | --- | --- |
| Quality policy | `python3 scripts/civic_quality_gate.py --policy .github/civic-quality-policy.json --strict .` | repository policy result | hosted CI and review |
| ABI/contracts | `python3 scripts/contract_check.py` | checked-in bindings/contracts | game assembly compatibility |
| Evidence fail-closed | `tests/test_wp01_evidence.py` | no fabricated WP01 pass | real licensed evidence |
| Deterministic/public tests | `python3 -m pytest -q` | public test suite | installed game behavior/performance |
| PR state | `gh pr list --repo KooshaPari/CivicSurvival-public ...` | live GitHub rollup | human approval and merge |

## Stop Conditions

- Do not edit Civic source without a coordinator handoff specifying path and
  SHA.
- Do not push, merge, auto-merge, reset, force-push, delete, prune, or rewrite
  the immutable archive ref without explicit protected-flow authorization.
- Treat an absent artifact ID, unsupported AgilePlus recording path, or
  licensed-host unavailability as a named blocker, not a reason to fabricate
  completion.
