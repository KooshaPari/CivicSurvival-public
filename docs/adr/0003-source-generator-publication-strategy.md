# ADR-0003: Source Generator Publication Strategy

- Status: Proposed
- Date: 2026-09-01
- Scope: `CivicSurvival.Analyzers`, WP01 licensed adapter build

## Context

The public snapshot deliberately excludes `CivicSurvival.Analyzers`, a private
Roslyn source generator project. These generators emit ~261 source files at
compile time (null-object patterns, feature manifests, UI lock-state
properties, persistence helpers). Without them, the main `CivicSurvival`
adapter project cannot compile, which blocks the WP01 licensed-host build,
launch smoke, and runtime verification steps.

The WP01 evidence manifest currently records `CONDITIONAL_NO_GO` with the
adapter build and launch smoke as the two blocking evidence records. All
audit-only gates (quality 12/12, tests 28/29, contracts build, OpenSSF
scorecard, dependency delta) pass.

BUILDING.md (lines 34-39) states:
> The project relies on a private set of Roslyn source generators (part of the
> CivicSurvival.Analyzers project) that are not published in this snapshot.

## Decision Paths

### Path A: Publish Source Generators (recommended for WP01 GO)

Extract `CivicSurvival.Analyzers` from the private repository, audit for
secrets/credentials/proprietary infrastructure references, and add to the
public snapshot as a new project in the solution.

- **Effort**: 1-2 hours audit + build verification
- **Impact**: Full end-to-end buildability; WP01 licensed adapter builds
  on any machine with the CS2 Modding Toolkit
- **Risk**: Low if audit is thorough; generators contain no runtime secrets
- **WP01 effect**: `CONDITIONAL_NO_GO` -> `CONDITIONAL GO` (pending runtime)

### Path B: Build from Private Repo, Attach Binaries

Build the adapter DLL in the private repository against the same SHA, then
attach `CivicSurvival.dll` + PDB as a GitHub Release artifact. Public
consumers verify the DLL hash against the published source.

- **Effort**: CI pipeline configuration
- **Impact**: Runtime evidence possible without publishing generator source
- **Risk**: Medium — binary-only verification is weaker than source audit
- **WP01 effect**: `CONDITIONAL_NO_GO` -> `CONDITIONAL GO` (binary-only)

### Path C: Publish Compiled Analyzer Binaries

Publish the compiled `CivicSurvival.Analyzers.dll` only (not source).
Enables third-party compilation without revealing generator internals.

- **Effort**: Low
- **Impact**: Partial buildability; harder to audit what generators emit
- **Risk**: Medium — cannot verify generator logic without source
- **WP01 effect**: Unclear — verifier may require source-level audit

### Path D: Accept Read-Only Snapshot (current state)

Document that the public snapshot is for auditability only. WP01 evidence
comes from the private build environment. The public surface proves contract
integrity and governance compliance but not end-to-end buildability.

- **Effort**: None
- **Impact**: Public consumers can audit contracts, quality gates, and
  governance but cannot reproduce the full build
- **Risk**: Low — this is the current and documented state
- **WP01 effect**: `CONDITIONAL_NO_GO` remains; blocker is by design

## Rationale

Path A is recommended because:
1. The generators produce compile-time artifacts, not runtime secrets
2. Full source auditability is the strongest evidence form
3. The WP01 evidence rules require machine-verifiable evidence, which
   Path B/C cannot fully satisfy
4. The blockers have been stable since the program's inception — resolving
   them would be the single most impactful improvement to the evidence surface

## Consequences

- Choosing Path A requires a security audit of the generator source before
  publication
- Path D is the safe default and maintains the current governance posture
- Regardless of path chosen, the framework mismatch (Blocker #1) has been
  resolved by PR #21 and is no longer a factor
- The `.civicignore` manifest already handles the CI limitation gracefully
  for the dependency delta scanner
