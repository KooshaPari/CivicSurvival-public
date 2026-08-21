---
spec_id: csv-009
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Balance Config Presets

**Slug**: csv-009-balance-config-presets | **Epic**: E9 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

Game balance is critical for survival difficulty curve. The balance_config.json (977 lines, auto-generated from YAML) defines all numerical parameters for crisis thresholds, resource rates, and difficulty scaling. Changes must be validated and versioned.

## Target Users

- Game designers tuning difficulty curves
- Mod developers adjusting balance parameters
- QA validating balance consistency across presets

## Functional Requirements

- [ ] **FR-BAL-001**: balance_config.json serves as single source of truth for all game balance parameters
- [ ] **FR-BAL-002**: YAML source files generate JSON via build pipeline; no manual JSON editing
- [ ] **FR-BAL-003**: 5 difficulty presets override base parameters with multiplier tables
- [ ] **FR-BAL-004**: Parameter validation on load; missing/invalid values fall back to safe defaults
- [ ] **FR-BAL-005**: Balance changes versioned in git; diff shows parameter changes clearly
- [ ] **FR-BAL-006**: Runtime balance hot-reload for development iteration
- [ ] **FR-BAL-007**: Balance presets exportable for community modding

## Non-Functional Requirements

- Config: `Config/balance_config.json` (977 lines, auto-generated)
- Source: YAML files in `Config/` (not yet committed)
- Validation: JSON Schema or custom validator
- No config changes at runtime without explicit reload

## Constraints and Dependencies

- Depends on: ModState (csv-001) for runtime consumption
- Depends on: DifficultyPresets (csv-001) for multiplier application
- Config must be backward-compatible across mod versions

## Acceptance Criteria

- [ ] balance_config.json contains all game balance parameters
- [ ] YAML → JSON generation pipeline works
- [ ] All 5 difficulty presets correctly override base parameters
- [ ] Invalid config values fall back to safe defaults with warning
- [ ] Config changes are git-diffable and versioned

## Status

| Story | Status |
|-------|--------|
| E9.1 Balance config structure | Complete |
| E9.2 YAML generation pipeline | Partial |
| E9.3 Difficulty preset overrides | Complete |
| E9.4 Config validation | Partial |
| E9.5 Version control | Complete |
| E9.6 Hot-reload | Partial |
| E9.7 Preset export | Planned |
