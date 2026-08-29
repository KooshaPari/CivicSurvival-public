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
4. `.agileplus/civic-warfare-program/tasks.md` and
   `.agileplus/civic-warfare-program/tasks/WP*.md`: WP scope, dependency
   order, and per-FR evidence record contract.
5. `.agileplus/civic-warfare-program/contracts/governance-program.md` and
   `contracts/governance-v1.json`: allowed state transitions and evidence
   semantics.
6. `.github/civic-quality-policy.json` and `.github/workflows/ci.yml`:
   repository quality rules and hosted gates.

## Work Package Cross-Reference

| WP   | Exact requirement IDs      | Repository-root-relative contract paths                                                                                                                             | Dependency boundary        |
| ---- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| WP01 | `FR-001..FR-005`, `FR-101` | `.agileplus/civic-warfare-program/tasks/WP01*`, `.agileplus/civic-warfare-program/wp01-evidence.template.json`, `.agileplus/civic-warfare-program/wp01-go-no-go.md` | Entry gate                 |
| WP02 | `FR-006..FR-010`, `FR-102` | `.agileplus/civic-warfare-program/tasks/WP02*`, `.agileplus/civic-warfare-program/contracts/`                                                                       | WP01                       |
| WP03 | `FR-011..FR-015`, `FR-103` | `.agileplus/civic-warfare-program/tasks/WP03*`                                                                                                                      | WP02                       |
| WP04 | `FR-016..FR-020`, `FR-104` | `.agileplus/civic-warfare-program/tasks/WP04*`                                                                                                                      | WP03                       |
| WP05 | `FR-021..FR-025`, `FR-105` | `.agileplus/civic-warfare-program/tasks/WP05*`                                                                                                                      | WP04                       |
| WP06 | `FR-026..FR-030`, `FR-106` | `.agileplus/civic-warfare-program/tasks/WP06*`                                                                                                                      | WP02, WP04, WP05           |
| WP07 | `FR-031..FR-035`, `FR-107` | `.agileplus/civic-warfare-program/tasks/WP07*`                                                                                                                      | WP03, WP04, WP06           |
| WP08 | `FR-036..FR-040`, `FR-108` | `.agileplus/civic-warfare-program/tasks/WP08*`                                                                                                                      | WP05, WP06, WP07           |
| WP09 | `FR-041..FR-045`, `FR-109` | `.agileplus/civic-warfare-program/tasks/WP09*`                                                                                                                      | WP04, WP07, WP08           |
| WP10 | `FR-046..FR-050`, `FR-110` | `.agileplus/civic-warfare-program/tasks/WP10*`                                                                                                                      | WP04, WP07, WP08           |
| WP11 | `FR-051..FR-055`, `FR-111` | `.agileplus/civic-warfare-program/tasks/WP11*`                                                                                                                      | WP04, WP07, WP08           |
| WP12 | `FR-056..FR-060`, `FR-112` | `.agileplus/civic-warfare-program/tasks/WP12*`                                                                                                                      | WP04, WP06, WP07, WP08     |
| WP13 | `FR-061..FR-065`, `FR-113` | `.agileplus/civic-warfare-program/tasks/WP13*`                                                                                                                      | WP05, WP07-WP12            |
| WP14 | `FR-066..FR-070`, `FR-114` | `.agileplus/civic-warfare-program/tasks/WP14*`                                                                                                                      | WP04, WP05                 |
| WP15 | `FR-071..FR-075`, `FR-115` | `.agileplus/civic-warfare-program/tasks/WP15*`                                                                                                                      | WP05-WP08, WP14            |
| WP16 | `FR-076..FR-080`, `FR-116` | `.agileplus/civic-warfare-program/tasks/WP16*`                                                                                                                      | WP03-WP08, WP13-WP15       |
| WP17 | `FR-081..FR-085`, `FR-117` | `.agileplus/civic-warfare-program/tasks/WP17*`                                                                                                                      | WP02, WP04-WP08, WP13-WP16 |
| WP18 | `FR-086..FR-090`, `FR-118` | `.agileplus/civic-warfare-program/tasks/WP18*`                                                                                                                      | WP02-WP08, WP13-WP16       |
| WP19 | `FR-091..FR-095`, `FR-119` | `.agileplus/civic-warfare-program/tasks/WP19*`                                                                                                                      | starts WP02; exits all     |
| WP20 | `FR-096..FR-100`, `FR-120` | `.agileplus/civic-warfare-program/tasks/WP20*`                                                                                                                      | WP01-WP19                  |

For every `FR-001..FR-120` and `QR-001..QR-020`, the mandatory record is:

```text
FR/QR ID -> WP -> implementation paths -> test IDs -> command/output hash
-> benchmark/security/license evidence -> review -> commit/PR
-> acceptance timestamp
```

The full FR text is intentionally not copied here. It is authoritative in
`.agileplus/civic-warfare-program/spec.md`; generated duplication would create
a second, stale requirements source. `QR-001..QR-020` apply across every WP;
their full text and the machine-governance rule are in that same specification
and in `.agileplus/civic-warfare-program/contracts/governance-v1.json`.

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

| Concern                    | Public command/source                                                                         | What it proves                | What remains external               |
| -------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------- |
| Quality policy             | `python3 scripts/civic_quality_gate.py --policy .github/civic-quality-policy.json --strict .` | repository policy result      | hosted CI and review                |
| ABI/contracts              | `python3 scripts/contract_check.py`                                                           | checked-in bindings/contracts | game assembly compatibility         |
| Evidence fail-closed       | `tests/test_wp01_evidence.py`                                                                 | no fabricated WP01 pass       | real licensed evidence              |
| Deterministic/public tests | `python3 -m pytest -q`                                                                        | public test suite             | installed game behavior/performance |
| PR state                   | `gh pr list --repo KooshaPari/CivicSurvival-public ...`                                       | live GitHub rollup            | human approval and merge            |

## Stop Conditions

- Do not edit Civic source without a coordinator handoff specifying path and
  SHA.
- Do not push, merge, auto-merge, reset, force-push, delete, prune, or rewrite
  the immutable archive ref without explicit protected-flow authorization.
- Treat an absent artifact ID, unsupported AgilePlus recording path, or
  licensed-host unavailability as a named blocker, not a reason to fabricate
  completion.
