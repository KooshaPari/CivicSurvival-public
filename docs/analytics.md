# Analytics

This document describes the **public, observable analytics surface** of
CivicSurvival -- the data we collect, where it goes, and who can see
it. This is the in-game / mod-side analytics; closed-source server
analytics are out of scope for this public repo.

## Three layers

### 1. In-game telemetry (`Domains/Telemetry/`)

The mod itself records:

| Metric | Where | Cardinality |
|---|---|---|
| Per-domain tick latency | `Telemetry/PerformanceWatchdog.cs` | low |
| Per-domain event rate | `Telemetry/EventCounter.cs` | low |
| Save write frequency + size | `Telemetry/SaveMetrics.cs` | low |
| Mod enable/disable churn | `Telemetry/ConfigChurnDetector.cs` | low |
| Crash detector verdict | `Telemetry/CrashDetector.cs` | rare |

These metrics are **stored only on the player's machine** in
`build-evidence/audit/` (see `docs/audit-log-spec.md`).

### 2. Optional opt-in telemetry (`Telemetry/SendPipeline.cs`)

If the player opts in via the in-game menu, the same data is
periodically sent to a community endpoint (Discord webhook, configurable
in `CivicSurvival/config/config.json`). The data is:

* Redacted (no player identifiers, no save contents).
* Hashed (sha256 of all stable identifiers).
* Bounded (max N events per session; see `SendPipeline.cs` rate limits).

The endpoint is **not** in this repository; it lives in the closed-source
operations repo. The public mirror only contains the client-side
send-pipeline code (`Telemetry/SendPipeline.cs`, `Telemetry/HttpClient.cs`).

### 3. Public scorecard metrics (`scripts/scorecard_ci.py`)

The 88-pillar scorecard is the **canonical public analytics surface**:
anyone can audit what the project has and intentionally does not have.
See `.github/scorecard-baseline.json` for the current baseline.

## What we do **not** collect

* Player username, IP, GUID.
* Save game contents.
* Raw keyboard/mouse input.
* Frequency of button presses.
* Anything beyond what is necessary to detect crashes and gameplay anomalies.

## How to opt out

In-game, the player sets `telemetry.send_enabled: false` in
`CivicSurvival/config/config.json` and clears the existing
`build-evidence/audit/` directory. No data is recorded or sent.

## For modders

If your mod calls into a `Telemetry/*` API, you are responsible for the
privacy properties of the data you pass in. The mod-side telemetry
**never** automatically captures third-party-mod events.

---

Last updated: 2026-09-01.
