# Monitoring

CivicSurvival does **not** have a server-side runtime to monitor.
What it does have is a **client-side observability pipeline** that
records in-game metrics to disk and (opt-in) sends a redacted summary
to a community endpoint.

## Two surfaces

### 1. Client-side observability

* Lives in `Domains/Telemetry/` (C# source).
* Hooks: per-domain `Tick`, `OnEvent`, `OnSave`, `OnLoad`.
* Storage: `build-evidence/audit/` (JSONL append-only files).
* See [`docs/audit-log-spec.md`](../audit-log-spec.md) for the format.

### 2. Public CI observability

This is what *this* repository's tooling actually publishes:

| Signal | Where | Notes |
|---|---|---|
| 88-pillar score | `scripts/scorecard_ci.py` output | displayed on every PR |
| Public-audit drift | `scripts/ci/check-public-audit.mjs` | fails the PR if csproj != manifest != publishConfig |
| Dependency delta | `scripts/dependency_delta.py` | tracks changes in `**/packages.lock.json` |
| Localization drift | `tests/test_localization_keys.py` | locks in 3,531-key parity across en-US/uk-UA/zh-CN |
| Baseline freshness | `tests/test_scorecard_baseline_freshness.py` (PR #58) | catches missing-file regressions |
| Release pipeline smoke | `tests/integration/test_release_pipeline.py` (this PR) | end-to-end version bump |

## What we do **not** monitor

* There is no uptime metric for this mirror (GitHub has its own).
* There is no SLI/SLO for the in-game mod; players see in-game
  performance via the per-frame rendering budget.
* There is no alerting endpoint; alerts surface in PR checks
  (`scripts/ci/check-public-audit.mjs`, `dependency_delta.py`).

## For modders

If your mod adds a telemetry-emitting event, declare it in the
`Telemetry/EventCounter.cs` event registry. The audit log spec
(`docs/audit-log-spec.md`) lists the existing event categories.

---

Last updated: 2026-09-01.
