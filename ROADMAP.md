# CivicSurvival Public -- Roadmap

This is the high-level roadmap for the **public, transparent source mirror**
of CivicSurvival. The full game (server, build pipeline, Paradox Mods
distribution) lives in the closed-source repository; only the in-game
client mod code is mirrored here for transparency and community review.

## What this repo is

* A 1,380-file C# Unity-mod source mirror with **no buildable distribution**
  (the CS2 Modding Toolkit is closed-source and not part of this repo).
* A CI/QA surface for the python tooling that wraps the C# source.
* A scorecard evidence layer (88-pillar audit) that documents what the
  repo has and intentionally does not have.

## Current focus

### 0.3.x -- Tooling & CI hardening (this cycle)

* [x] Localization regression suite (`tests/test_localization_keys.py`)
* [x] Public-audit drift detection across csproj/manifest/PublishConfig
* [x] Scorecard baseline lock-in (`chore/scorecard-baseline-0.3.25`)
* [x] CI gating hardening (CodeQL, gitleaks, audit-ci, ruff, prettier)
* [x] Community profile files (CoC, SECURITY, SUPPORT, templates)
* [x] Atomic release CLI (`scripts/release.py`)
* [x] Self-discovering LEGIT_IDENTICAL allowlist (`test_localization_keys.py`)
* [x] Dependency delta scanner with metadata-only exemption
* [x] Tier A tooling (Makefile, Justfile, pyproject, .releaserc)
* [x] Fuzz/bench/integration/stress test infrastructure
* [ ] Tier B docs (ROADMAP, feedback, feature-flags, audit-log, license-checker, analytics)

### 0.4.x -- Domain depth & telemetry

* [ ] Wire the existing telemetry pipeline to surface scoring metrics
      to the in-game dashboard (`Domains/Telemetry/Systems/`).
* [ ] Promote `services/arena/` event types into stable contracts
      (`Contracts/`) so external lobby servers can subscribe.
* [ ] Multi-locale expansion: add `es-ES`, `fr-FR`, `de-DE` locales
      (`CivicSurvival/Localization/`). Requires translator volunteers.
* [ ] Localization reconciliation tooling: detect near-duplicate keys
      that should be merged (e.g. `*_BUTTON_LABEL` vs `*_LABEL_BTN`).

### 0.5.x -- Mod-compatibility surface

* [ ] Document the public mod-compatibility API: which `Domain` events
      are stable, which are pending, which are private.
* [ ] Add `samples/` directory with minimal example mods that exercise
      each public surface.
* [ ] Run the existing Harmony patches through an automation matrix
      against the next CS2 patch tier.

### 1.0.x -- Community open-source release

* [ ] Tag a 1.0.0 release when the public surface contracts are stable.
* [ ] Move closed-source-only artifacts (the full Paradox Mods upload,
      the auto-test fuzz farm) to a separate repo with restricted access.
* [ ] Inaugurate a community advisory board for breaking-change review.

## Anti-roadmap

These are explicit **non-goals** for this public repo:

* **Bug-tracker parity with the closed repo.** All gameplay-impacting
  bugs live in the closed repo and are triaged there. This repo only
  surfaces modder-visible regressions.
* **Player-visible release notes.** Player-facing changes are documented
  in the closed repo and ship through the Paradox Mods launcher.
* **Migrating proprietary modules here.** The game-server code, the
  Paradox upload pipeline, and the auto-test fuzz farm stay closed.

## How to influence this roadmap

* Open an issue using the
  [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
  and tag `@KooshaPari`.
* For substantial direction changes, comment on the relevant PR or
  open a discussion with the rationale.
* Discord-first triage route is documented in [SUPPORT.md](SUPPORT.md).

---

Last updated: 2026-09-01 (v0.3.25).
