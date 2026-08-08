# Civic Warfare Program Memory and Anti-Drift Ledger

## Sponsor Goal

Audit CivicSurvival in extreme depth and evolve it into a state-of-the-art, fully configurable grand-theater city-survival game where city building, economy, infrastructure, population, politics, and logistics materially sustain defense and warfare across ground, air, sea, covert, civil, and diplomatic domains.

## Sponsor Prompts and Ideas Preserved

- Evaluate quality, audit gaps, refactors, improvements, polish, optimization, QoL, and features using subagents and web research.
- Add proper ground, air, sea, invasion, defense, armies, walls, bases, military infrastructure, foreign settlements, factions, diplomacy, spies, terrorism, corruption, riots, protests, occupation, and peace.
- Make city building and a deeper firm/contract economy support defense rather than exist beside it.
- Use operational command, not per-unit RTS control; make the real city and persistent War Room co-primary.
- Support manual, advisory, semi-autonomous, and autonomous play per domain.
- Support sandbox/objectives, finite campaigns, and endless escalation from one configurable core.
- Use neutral systemic English plus realistic Ukrainian localization/context; retain uk-UA and new zh-CN parity.
- Use rule-symmetric factions with adaptive detail: exact detailed simulation near consequential events and exact-conserving aggregation elsewhere.
- Default Grand Theater scale: about 12 factions, 60 settlements, and 300 formations.
- Use maximum beneficial polyglotting and borrowing/wrapping over hand-rolling, while requiring each language/library to own an isolated artifact and prove measurable benefit.
- Consider hexagonal architecture and other patterns deliberately; do not reject necessary architecture as YAGNI.
- Accept copyleft and whole-project relicensing if a dependency provides decisive leverage, but require a provenance/license ADR first.
- Use AgilePlus CLI and its spec/artifact system for the full plan, end-to-end DAG/WBS, governance, and continuously updateable progress.
- Fork before substantive artifact publication.

## Locked Decisions

1. Fork `KooshaPari/CivicSurvival-public`; preserve `Theorist100/CivicSurvival-public` as upstream.
2. Branch/worktree: `feat/civic-warfare-program` in `CivicSurvival-public-wtrees/civic-warfare-program`.
3. Rust authoritative deterministic runtime; C# Unity/ECS host; TypeScript/React UI; Python/Julia offline; Zig build candidate; Mojo experimental; Nim/Pony/Vale research only.
4. Modular monolith; functional core/imperative shell; hexagonal ownership boundaries; bounded contexts; commands plus immutable projections; snapshots plus selective command/outcome journal.
5. No Rust-side generic ECS, authoritative actor model, blanket event sourcing, microservices, runtime neural agent, or live LP/MIP solver.
6. Interoptopus + pinned FlatBuffers boundary; fixed-point authority; canonical BLAKE3 replay hashes.
7. Selective detail must preserve canonical quantities exactly; no fake distant simulation.
8. Forward-only warfare save schema with no development-save compatibility shims.
9. Production warfare implementation is blocked until WP01's public audit build, baseline C# tests, CI, and quality gate pass.
10. Exactly 20 aligned AgilePlus work packages and 120 functional requirements; six requirements per WP because installed AgilePlus v0.2.1 batches at that granularity.

## Canonical Artifacts

- `spec.md`: complete 120-FR and 20-quality-requirement product specification.
- `research.md`, `research/source-register.csv`, `research/evidence-log.csv`: grounded audit, sources, and decisions.
- `plan.md`, `tasks.md`, `tasks/WP*.md`: 20-lane WBS, parallel DAG, entry/exit evidence, and work prompts.
- `architecture.md`, `data-model.md`, `contracts/`: technical boundaries and public contracts.
- `dashboard.md`, `contracts/governance-v1.json`, `contracts/governance-program.md`: live status and gate policy.
- `docs/sessions/20260722-civic-warfare-program/`: required session indexes and known issues.

## Current State

- Audit/research: complete for v0.3.24 snapshot `0b218074`.
- Specification: complete and registered; 120 FRs.
- AgilePlus: 20 WPs registered in ignored operational DB `.agileplus/civic-warfare-program-v4.db`.
- Canonical DAG/WBS: complete; CLI's false fully serial overlap graph is superseded by `plan.md`.
- Architecture/data model/public contracts: complete for planning baseline.
- Governance/dashboard/checklist/validation: complete; branch publication complete.
- WP01: public audit green; conditional NO-GO remains for production warfare until licensed adapter and AgilePlus evidence paths exist.
- WP02-A reconnaissance: native workspace absent; ABI/schema risks recorded in `wp01-go-no-go.md`.
- WP02-A boundary slice: pinned Rust workspace now exists under `native/` with five inward-directed crates and locked smoke tests; FlatBuffers/FFI implementation remains pending.
- WP02-A contract hardening: status now uses caller-owned serialized bytes (`csw_status_into`), FlatBuffers are framed by `Envelope`/`RootPayload`, and projection deltas expose removals, alerts, and explanations; static boundary checks pass while pinned `flatc` conformance remains pending.
- WP02-A FFI slice: `civic-ffi` now exports a panic-contained no-op lifecycle as `cdylib`/`rlib`, with bounded buffer and handle tests; it deliberately does not claim FlatBuffers decoding or gameplay.
- WP02-A ABI smoke: `tests/wp02/test_ffi_abi.sh` links `ffi_smoke.c` against the produced cdylib and passes; load/submit/poll/save remain explicit stubs pending generated verifier integration.
- WP02-A generated verification: pinned `flatc` plus exact Rust `flatbuffers` runtime now validates a real `CSWP` Envelope and rejects truncation and bad identifiers; local Homebrew `flatc 25.12.19` reproduced the gate.
- WP02-A FFI verifier integration: `native/ffi/build.rs` generates bindings at build time and `civic-ffi` now rejects malformed nonempty config/save/command envelopes as `CSW_SCHEMA_MISMATCH` or `CSW_CORRUPT_DATA`; empty bootstrap buffers remain allowed.
- WP02-A payload typing: `csw_load` now requires `RootPayload::SaveEnvelope` and `csw_submit_commands` requires `RootPayload::CommandBatch`; generic Envelope validation remains separate from authoritative decode/serialization.
- WP02-A semantic gates: SaveEnvelope versions are checked against ABI/schema/save/RNG version 1 and required save vectors must be present; command batches require schema version 1. Failed create paths clear the caller output handle before returning.
- WP02-A transactional load: minimal valid SaveEnvelope and CommandBatch vectors now pass; load constructs a temporary runtime with saved tick/revision and publishes the handle only after version, required-vector, and fixed-width hash/ID checks.
- Gameplay implementation: intentionally not started.

## Anti-Drift Rules

- Never shrink the full program into air defense only, tactical RTS only, or a cosmetic War Room.
- Never disconnect military capability from firms, workers, population, utilities, transport, imports, finance, corruption, and legitimacy.
- Never give AI hidden truth, free resources, mutation backdoors, or unexplained decisions.
- Never handwave ground, air, sea, invasion, occupation, intelligence, unrest, or peace as later placeholders.
- New ideas are triaged into the appropriate WP/FR/evidence record; they do not silently replace approved scope.
- Progress changes only from AgilePlus WP state plus linked acceptance evidence.

## Next Meaningful Work

1. Close the AgilePlus evidence-recording gap without direct database fabrication.
2. Obtain licensed game-adapter build and launch-smoke evidence.
3. Begin WP02-A native ABI, schema, FFI, and golden-vector boundary work.
4. Keep production warfare implementation closed until WP01 is formally accepted.
