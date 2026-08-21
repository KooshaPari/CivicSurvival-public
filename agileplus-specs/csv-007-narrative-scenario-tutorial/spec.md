---
spec_id: csv-007
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Narrative Scenario Tutorial

**Slug**: csv-007-narrative-scenario-tutorial | **Epic**: E7 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The mod provides narrative context through scenarios, tutorials, and event chains. The Narrative domain manages story progression and event triggers. The Scenario domain provides pre-configured game setups. The Tutorial domain guides new players through mod mechanics.

## Functional Requirements

- [ ] **FR-NAR-001**: Narrative domain manages story events, triggers, and progression state
- [ ] **FR-NAR-002**: Scenario domain provides pre-configured difficulty/reward profiles (balance presets)
- [ ] **FR-NAR-003**: Tutorial domain provides step-by-step guidance for new players
- [ ] **FR-NAR-004**: Narrative events integrate with all game domains for context-aware triggers
- [ ] **FR-NAR-005**: Scenario configurations persist in save format; load validates compatibility
- [ ] **FR-NAR-006**: Tutorial progression saved per-player; resumable across sessions
- [ ] **FR-NAR-007**: Narrative UI overlays story elements without blocking gameplay

## Non-Functional Requirements

- Domains: `Narrative/`, `Scenario/`, `Tutorial/`
- Narrative triggers must not cause tick budget overruns
- Tutorial state lightweight and non-persistent when disabled

## Constraints and Dependencies

- Depends on: ModState (csv-001)
- Depends on: All domains for context-aware narrative triggers
- Tutorial must not interfere with experienced player workflows

## Acceptance Criteria

- [ ] Narrative events trigger correctly based on game state
- [ ] All 5 difficulty presets correctly configure game parameters
- [ ] Tutorial steps progress correctly and skip gracefully
- [ ] Scenario load validates all required mod components
- [ ] Narrative UI renders without frame drops

## Status

| Story | Status |
|-------|--------|
| E7.1 Narrative event system | Complete |
| E7.2 Scenario presets | Complete |
| E7.3 Tutorial system | Partial |
| E7.4 Domain integration | Complete |
| E7.5 Save/load validation | Complete |
| E7.6 Tutorial persistence | Partial |
| E7.7 Narrative UI | Complete |
