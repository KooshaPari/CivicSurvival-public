# Audit Log Specification

CivicSurvival records an audit trail for everything that affects game
state, save files, and player-visible behaviour. This document is the
specification of what gets logged, where, and how long it is retained.

## Goals

1. **Reproducibility** -- given a save file and an audit-log segment,
   any modder (or future contributor) can replay the relevant events.
2. **Modder-friendly diagnostics** -- when a third-party mod breaks
   gameplay, the audit log provides a single timeline of which events
   fired in which order.
3. **Forensics for telemetry/crashe-detection** -- the
   `Telemetry/CrashDetector` and `Telemetry/SendPipeline` systems
   emit audit events when they suspect a crash pattern.

## What gets logged

| Event category | Location | Format |
|---|---|---|
| Domain tick boundary | `Domains/*/Domain.cs::Tick()` | `tick:N domain:M state_hash:H` |
| Save file write | `Core/Persistence/SaveWriter.cs` | `save_write:N size:B sha256:H` |
| Save file load | `Core/Persistence/SaveLoader.cs` | `save_load:N size:B sha256:H status:S` |
| Configuration change | `Core/Configuration/ConfigManager.cs` | `config_set key:K old:V new:V` |
| User input | `Core/Input/InputRouter.cs` | `input:E bound_to:A` |
| Locale change | `Localization/LocalizationManager.cs` | `locale_change from:F to:T` |
| Network event | `Networking/NetworkManager.cs` | `net_send:N net_recv:N` |
| Crash detector | `Telemetry/CrashDetector.cs` | `crash_suspect pattern:P frame_count:F` |
| Performance alert | `Telemetry/PerformanceWatchdog.cs` | `perf_alert metric:M value:V threshold:T` |

## Storage layout

Audit logs are append-only JSONL files under `build-evidence/audit/`:

```
build-evidence/audit/
  2026-09-01/                  # date partition
    civic-20260901-153000.jsonl  # session file: timestamped on startup
    civic-20260901-170000.jsonl
  index.jsonl                  # rollup: one line per session, sha256 of each file
```

The `index.jsonl` is the authoritative manifest for the audit trail; it
is itself signed by the build system if `EnableDiagnostics` is on.

## Retention

| Tier | Retention | Notes |
|---|---|---|
| Local dev | 7 days | honour `.gitignore`; not committed |
| Telemetry send pipeline | 30 days | redacted before send |
| Crash detector verbatim | 90 days | used by `CrashDetector` repeat-pattern detection |
| Public mirror | permanent (this repo) | `build-evidence/audit/` is gitignored, **not** committed |

## Privacy

Audit logs **never contain**:

* Player identifiers (username, IP, GUID) beyond a session-local token.
* Save game contents (only sha256 hashes are recorded).
* Raw input -- only the *binding* is recorded, not the press duration.

These guarantees are enforced by the unit tests in
`tests/test_localization_keys.py` (the closest existing test layer)
and audited manually before each release by the maintainer.

---

Last updated: 2026-09-01.
