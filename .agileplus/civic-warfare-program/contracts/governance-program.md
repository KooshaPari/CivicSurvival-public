# Program Governance Contract

## State Transitions

`planned -> doing -> review -> done`; `blocked` requires a named blocker, owner, evidence, and next review. Entry dependencies in `plan.md` must be done before `doing`, except only the named `WP17.projection-primitives`, `WP18.authoring-tools`, and `WP19.harness-foundation` scopes after WP02.

The CLI-generated `governance-v1.json` is retained as machine-readable baseline policy. Its generic `FR-CI` and `FR-REVIEW` evidence labels are tool vocabulary, not program requirements; this contract and the real `FR-001` through `FR-120` traceability records govern acceptance.

## Required Evidence for Doing -> Review

- Six FR evidence records with implementation paths and test IDs.
- Focused unit/property/contract test output.
- Integration/replay/UI evidence required by the lane.
- Architecture and <=500-line module checks.
- Security, license, privacy, and localization impact assessment.
- Performance comparison against the prior accepted baseline.
- Updated public contracts, docs, and known issues.

## Required Evidence for Review -> Done

- Independent code and specification review approval.
- Full affected-suite green evidence and deterministic replay hash where authoritative state changes.
- No unresolved critical/high correctness, security, privacy, data-loss, or determinism finding.
- All review findings fixed forward or recorded as accepted non-blocking risk with owner.
- Commit/PR reference, artifact hashes, and Airlock snapshot reference.

## Special Gates

- WP01 completion is required before any production warfare implementation merge. Completion requires public audit/build/tests, licensed adapter build and launch smoke, artifact hashes/provenance, and supported AgilePlus evidence recording; see `wp01-go-no-go.md`.
- ABI/schema/save/RNG/rules changes require version and conformance evidence.
- Copyleft import or relicensing requires a separate accepted ADR and provenance dossier.
- WP19 must ingest every FR evidence record before WP20 can enter review.
- WP20 requires all 120 FRs and 20 quality requirements accepted.

## Progress

WP completion is accepted-FRs divided by six. Program functional progress is accepted-FRs divided by 120. Quality progress is passed mandatory gates divided by total mandatory gates. Time spent, files changed, or commits made never count as acceptance.
