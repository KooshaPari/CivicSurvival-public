# CivicSurvival WP01 Runner Portability Snapshot

- **Date (UTC)**: 2026-09-01T15:39:00Z
- **Branch**: docs/civic-reconciliation-governance-hard-stop-20260901
- **Head commit**: 92b448357fe2b5820f2afa2c219b52d318a4e9ca
- **Fork**: KooshaPari/CivicSurvival-public
- **Upstream**: Theorist100/CivicSurvival-public

## Change

CivicSurvival.PublicAudit/CivicSurvival.PublicAudit.csproj now targets
net8.0 with LatestMajor roll-forward. The runner previously required
the .NET 9 runtime, which is not commonly installed on contributor
hosts; the new target executes on any installed .NET 8/9/10 runtime
while still compiling against the same public-SDK contracts surface.

## Verification

- `bash tests/public-audit/test_contracts_build.sh` -> PASS (both
  net8.0 and net48 targets build without private toolchain imports).
- `bash tests/public-audit/test_runner.sh` -> PASS
  ({"status":"pass","contractsBuild":"pass","localizationParity":"pass","sourceRoots":"pass"}).
- All three audit gates green on a fresh macOS arm64 host with .NET
  10.0.10 runtime only.

## Commits

- 4416a60 docs(civic): mark GLM handoff resume point and active branch
- a128593 build(public-audit): target net8.0 with LatestMajor roll-forward
- 92b4483 docs(civic): record WP01 runner portability fix and program state

## Program state

- WP01 public-audit lane: green
- WP01 production-warfare gate: still closed (awaiting licensed
  game-adapter evidence and AgilePlus evidence-recording path)
- WP02-A native ABI/schema slice: not started (gated by WP01 acceptance)
