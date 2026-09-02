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
- WP02-A: A 4th public-audit gate (FlatBuffers schema contract check)
  is added to `CivicSurvival.PublicAudit/Program.cs`. The gate
  validates the `.agileplus/civic-warfare-program/contracts/warfare.fbs`
  schema and `civic_warfare.h` header:
  - required enum members present (NoOp, SetPolicy, SetMission, etc.)
  - required enum members present in DecisionCode
  - file_identifier present and CSWP
  - root_type present and CommandDispatch
  - required csw\_\* ABI functions declared (csw_init, csw_status_into,
    csw_poll_into, csw_arena_command, csw_warfare_faction_snapshot)
  - no ColossalOrder proprietary references in public header
    A regression test `tests/public-audit/test_flatbuffers_contract_drift.sh`
    proves all 5 mutation cases (shrunk enum member, changed file_identifier,
    removed ABI function, proprietary reference injection) are caught.
    All 4 public-audit gates pass: contracts build, localization parity,
    source roots, flatbuffersSchema.
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

1. PR #81 CI is FULLY GREEN as of this writing: Analyze (csharp),
   Analyze (javascript-typescript), Lint & Format, public-audit x2,
   scorecard, semgrep-cloud-platform/scan, Socket Security x2 all pass.
   Kilo Code Review is pending. Await final Kilo review and any
   remaining CodeRabbit review before merge consideration.
2. Obtain licensed game-adapter build and launch-smoke evidence on a
   Windows/CS2 host; attach the artifact-hash and provenance chain to
   `wp01-go-no-go.md` and re-promote the WP01 decision to GO.
3. After PR #81 lands, prepare a successor WP02-A PR from current
   `origin/main` with test-first ABI/schema/golden-vector evidence
   for the FlatBuffers boundary: native-side reader golden vectors,
   C# deserialization path, and end-to-end roundtrip test using
   the Rust test-vector generator.
4. The `test_flatbuffers_contract_drift.sh` regression test must
   be extended as the schema grows: every new enum member, struct
   field, and ABI function added to the public contracts must have
   a corresponding `check_contracts.sh`-style test that proves
   removal is detected.
5. Resolve the pre-existing C# solution NuGet "Invalid framework
   identifier" error (out of scope for PR #81; recorded for the
   next housekeeping PR after PR #81 lands).
6. Keep production warfare implementation closed until WP01 is formally
   accepted and Kilo/CodeRabbit reviews confirm no governance concerns.
