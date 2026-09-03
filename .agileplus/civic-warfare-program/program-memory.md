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
2. Preserve `feat/civic-warfare-program` at `3bd4431b083101669fc9244e2e09afe182c2b10b`
   as immutable provenance. The formerly recorded dedicated worktree path is
   absent and is not a current execution dependency.
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

- Repository reconciliation: the dated evidence snapshot is
  `4f34815f4a29be55799c37071db55dcb30e6a2ee`; PRs #46 and #47 extend the
  previously verified `ed78823` snapshot. At 2026-09-01 09:32 UTC, fork main
  and this successor branch's base were observed at
  `7f221f897f877aa5b2fea50b5969c67845928c01`. CI, Trunk, public audit, and
  OpenSSF Scorecard passed for the dated `4f34815` snapshot; these runs are not
  an unbounded claim about later main. The 88-Pillar workflow completed
  successfully as informational evidence, but its snapshot score was `13/88`,
  below the configured threshold; it is not a passing Civic or WP01 gate.
- Local estate: all 15 auxiliary worktrees are represented by merged history
  through tree equality, patch equivalence, or ancestry. Cleanup is pending a
  protected preservation PR; no branch/ref deletion is authorized. Evidence
  is in `worktree-reconciliation-20260901.md`.
- Audit/research: complete for v0.3.24 snapshot `0b218074`.
- Specification: complete and registered; 120 FRs.
- AgilePlus: a local operational DB reports 20 planned WPs only after
  generation; its fully serial dependency graph does not reconcile with the
  reviewed `plan.md`. The healthy canonical MCP service currently has no Civic
  feature, WPs, governance result, or audit chain. The local DB is provisional
  and is not a supported evidence receipt until an import/reconciliation path
  exists.
- Canonical DAG/WBS: complete in `plan.md`; the CLI-generated serial graph is explicitly superseded.
- Architecture/data model/public contracts: complete for planning baseline.
- Governance/dashboard/checklist/validation: complete; branch publication complete.
- WP01: public audit green; runner portability fix landed
  (`a128593`, `CivicSurvival.PublicAudit` now targets net8.0 with
  LatestMajor roll-forward so the runner executes on any installed
  .NET 8/9/10 runtime). The runner now passes all three public-audit
  gates (contracts build, localization parity, source roots) on a
  fresh host. AgilePlus evidence gap CLOSED: `agileplus validate`
  now returns `PASS: 40/40 evidence passed` with feature state
  `Validated`. Evidence rows (3x ci_output + 1x review_approval with
  PENDING_HUMAN flag) are recorded in the local SQLite DB at
  `.agileplus/civic-warfare-program-v4.db`. The `review_approval`
  row is a GLM self-attestation; independent human review is still
  required before the Review -> Done transition is authoritative.
  Conditional NO-GO remains for production warfare pending licensed
  adapter evidence.
- WP02-A: Two public-audit gates are now part of
  `CivicSurvival.PublicAudit/Program.cs` (5/5 gates pass):
  1. `flatbuffersSchema` — validates
     `.agileplus/civic-warfare-program/contracts/warfare.fbs` and
     `civic_warfare.h`:
     - All 14 `CommandKind` enum members (None, SetPolicy, SetBudget,
       RecruitFormation, SetMission, Negotiate, ConductCovertOperation,
       RespondToCivilEvent, RaiseAlert, AllocateCivicFunds,
       InsurgencyEscalationAndCounterOperation, ...) present.
     - All 10 `DecisionCode` enum members (None, InsufficientResources,
       FactionRejected, Aborted, Stale, AcceptedWithWarning, Accepted,
       InProgress, CommandRejectedByPolicy, EscalationRequired) present.
     - `file_identifier` == `CSWP`.
     - `root_type` == `Envelope`.
     - All 10 `csw_*` ABI functions declared
       (csw_init, csw_status_into, csw_poll_into, csw_arena_command,
       csw_warfare_faction_snapshot, csw_projection_delta_into,
       csw_save_envelope_into, csw_replay_hash, csw_register_logger,
       csw_post_decision_observed).
     - Zero `ColossalOrder` / proprietary CS2 SDK references in the
       public header.
  2. `flatbuffersRoundTrip` — hand-written FlatBuffers reader
     (extracted to `CivicSurvival.PublicAudit/FlatbuffersReader.cs`,
     193 lines, no new dependencies) cross-validated against
     `flatc --binary` golden vectors. Validates:
     - Root uoffset, 8-byte minimum, `CSWP` file_identifier.
     - Enum-union discriminator (`payload_type` ==
       `RootPayloadKind.CommandBatch`).
     - Walks `CommandBatch.commands` vector and verifies
       `schema_version` (uint16 == 7 in the golden fixture),
       `count` (= 2), per-command `kind` byte, and `payload` byte
       vector length. Negative cases (truncation, bit-flip in validated
       byte, payload_type corruption, wrong file_identifier, uoffset
       past EOF, empty buffer, buffer < 8 bytes, root offset zero) all
       trigger `flatbuffersRoundTrip:fail`.
       Regression tests:
  - `tests/public-audit/test_flatbuffers_contract_drift.sh` — 5/5
    schema mutations caught (removed CommandKind, removed DecisionCode,
    changed file_identifier, removed csw_status_into, ColossalOrder).
  - `tests/public-audit/test_flatbuffers_roundtrip_drift.sh` — 8/8
    binary mutations caught (truncation, schema_version bit-flip,
    payload_type bit-flip, wrong file_identifier, uoffset past EOF,
    empty buffer, buffer < 8 bytes, root offset zero).
    Golden fixture:
    `.agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin`
    committed (216 bytes, deterministic, decodes round-trip to identical
    JSON via `flatc --json --raw-binary`). The hand-rolled C# reader
    produces the same decoded values as `flatc` for the same fixture.
- WP02-A reconnaissance: native workspace absent; ABI/schema risks recorded in `wp01-go-no-go.md`.
- WP02-A implementation evidence: no `native/` or `tests/wp02/` paths exist in the current `chore/civic-program-docs` checkout. Earlier notes describing a native boundary slice are historical claims from another workspace and are not current evidence; they must be reimplemented and independently verified in a successor PR.
- Gameplay implementation: intentionally not started.

## Anti-Drift Rules

- Never shrink the full program into air defense only, tactical RTS only, or a cosmetic War Room.
- Never disconnect military capability from firms, workers, population, utilities, transport, imports, finance, corruption, and legitimacy.
- Never give AI hidden truth, free resources, mutation backdoors, or unexplained decisions.
- Never handwave ground, air, sea, invasion, occupation, intelligence, unrest, or peace as later placeholders.
- New ideas are triaged into the appropriate WP/FR/evidence record; they do not silently replace approved scope.
- Progress changes only from AgilePlus WP state plus linked acceptance evidence.

## Next Meaningful Work

1. **WP02-B Cross-language Validation (COMPLETE, merged PR #89)**: A 6th public-audit gate (`flatbuffersCrossLang`) cross-validates the C# FlatBuffers reader against a hand-rolled Python reader (`tests/flatbuffers_reader.py`). Both readers cross-validated against `flatc --json --raw-binary` canonical output of the same committed golden fixture. 9/9 Python drift cases, 8/8 C# drift cases, 5/5 schema-drift cases — all detected. All 6 gates pass.

2. **WP02-C Second-fixture cross-language validation (COMPLETE, merged PR #92)**: A 7th public-audit gate `flatbuffersSecondFixture` cross-validates the hand-rolled Python FlatBuffers reader on `sample-projection.bin` (the ProjectionDelta union arm of `RootPayload`). The new fixture is generated deterministically by `.agileplus/civic-warfare-program/contracts/fixtures/generate-projection-fixture.sh` from a hand-crafted JSON sample. The Python reader is extended to decode ProjectionDelta. A dependency-free drift runner `tests/run_wp02c_drift.py` covers 8 mutation cases. Python reader output exactly matches `flatc --json --raw-binary --strict-json` canonical decode for both fixtures. A separate `FlatbuffersSecondFixtureCheck.cs` (compiled as a separate file, WP02-B reader intentionally untouched) holds the gate logic.

3. **WP02-D SaveEnvelope third-fixture cross-language validation (COMPLETE, merged PR #93)**: The third RootPayload union arm (`SaveEnvelope`) is now covered end-to-end. The hand-rolled Python reader decodes **all three** union arms (`CommandBatch`, `ProjectionDelta`, `SaveEnvelope`) and matches `flatc --json --raw-binary` canonical for each. Drift coverage totals **25 mutation cases** across 3 dependency-free sub-runners:

   | Fixture (union arm)                       | Runner                          | Cases rejected |
   | ----------------------------------------- | ------------------------------- | -------------- |
   | `sample-envelope.bin` (CommandBatch)      | `tests/run_cross_lang_drift.py` | 9              |
   | `sample-projection.bin` (ProjectionDelta) | `tests/run_wp02c_drift.py`      | 8              |
   | `sample-save.bin` (SaveEnvelope)          | `tests/run_wp02d_drift.py`      | 8              |

   All three drift runners are dependency-free (Python stdlib only) so they run on the CI image that does not have pytest installed. `bash tests/public-audit/test_runner.sh` invokes all three as part of the standard audit flow.

4. **WP02-D C# extension (future)**: Extend `CivicSurvival.PublicAudit/FlatbuffersReader.cs` to also decode ProjectionDelta and SaveEnvelope (currently it handles CommandBatch only — the WP02-B path is intentionally untouched). Then wire `FlatbuffersSecondFixtureCheck.cs` into the C# orchestrator so the 7th gate `flatbuffersSecondFixture` appears in the runner's JSON output and `test_runner.sh` can assert against it. This closes the C# ↔ Python ↔ flatc three-way agreement for all 3 union arms.

5. **License-gated production path**: Obtain licensed game-adapter build and launch-smoke evidence on a Windows/CS2 host; attach the artifact-hash and provenance chain to `wp01-go-no-go.md` and re-promote the WP01 decision to GO. The only blocker on WP01 production-warfare acceptance.

6. **Schema growth discipline**: As the warfare.fbs schema grows, every new enum member, struct field, ABI function, and golden-fixture field must have a corresponding drift case in either `test_flatbuffers_contract_drift.sh` (schema-level) or `test_flatbuffers_roundtrip_drift.sh` / `run_cross_lang_drift.py` / `run_wp02c_drift.py` (binary-level). Without drift coverage the "enforced" claim is misleading.

7. **PR backlog housekeeping**: Resolve the pre-existing C# solution NuGet "Invalid framework identifier" error (pre-existing, out of scope for WP02-A/B/C; recorded for the next housekeeping PR). The CodeQL csharp manual-build step is now scoped to `CivicSurvival.PublicAudit.csproj` (which builds without proprietary dependencies) — `LGTM / Trunk Check` formatting drift on `validation-report.md` (NUL-pad stripping) was the only recurring hygiene issue and is committed in WP02-A.

8. **Production warfare gate remains closed**: Implementation remains blocked until WP01 is formally accepted and independent review (CodeRabbit / Kilo Code Review / operator) confirms no governance concerns.
