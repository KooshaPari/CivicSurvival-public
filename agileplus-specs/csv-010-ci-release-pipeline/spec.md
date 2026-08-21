---
spec_id: csv-010
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: CI Release Pipeline

**Slug**: csv-010-ci-release-pipeline | **Epic**: E10 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The mod requires automated CI/CD for build validation, testing, and release to Paradox Mods. The pipeline must handle C# compilation, TypeScript UI build, integration testing, and Paradox Mods publishing.

## Target Users

- Developers pushing code changes
- Release managers publishing to Paradox Mods
- QA validating builds before release

## Functional Requirements

- [ ] **FR-CI-001**: GitHub Actions CI runs on every PR: C# build, TypeScript build, linting, tests
- [ ] **FR-CI-002**: Trunk Check enforces code quality (formatting, linting, security) across C# and TypeScript
- [ ] **FR-CI-003**: OpenSSF Scorecard workflow tracks security posture
- [ ] **FR-CI-004**: Infisical Sync workflow manages secrets rotation
- [ ] **FR-CI-005**: CircleCI provides parallel build pipeline for faster feedback
- [ ] **FR-CI-006**: Release workflow packages mod and publishes to Paradox Mods (#147665)
- [ ] **FR-CI-007**: Renovate bot manages dependency updates with auto-merge for patch versions

## Non-Functional Requirements

- CI: `.github/workflows/` (5 workflows)
- CI: `.circleci/` (parallel pipeline)
- CI: `.trunk/` (Trunk.io config)
- Build artifact: `.cs2mod` package for Paradox Mods
- Release: SemVer versioning aligned with CS2 game versions

## Constraints and Dependencies

- Depends on: CS2 game assemblies for C# compilation (via NuGet or game install)
- Paradox Mods API for publishing (requires auth tokens)
- CI must not expose game DLLs or proprietary assets

## Acceptance Criteria

- [ ] All 5 CI workflows pass on main branch
- [ ] Trunk Check passes with zero violations
- [ ] OpenSSF Scorecard score >= 8/10
- [ ] Renovate auto-merges patch dependency updates
- [ ] Release workflow produces valid .cs2mod package
- [ ] Paradox Mods publishing succeeds with correct version

## Status

| Story | Status |
|-------|--------|
| E10.1 GitHub Actions CI | Complete |
| E10.2 Trunk Check | Complete |
| E10.3 OpenSSF Scorecard | Fixed (permissions) |
| E10.4 Infisical Sync | Complete |
| E10.5 CircleCI parallel | Complete |
| E10.6 Release workflow | Partial |
| E10.7 Renovate config | Complete |
