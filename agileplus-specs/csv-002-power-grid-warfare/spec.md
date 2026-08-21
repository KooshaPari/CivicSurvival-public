---
spec_id: csv-002
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Power Grid Warfare

**Slug**: csv-002-power-grid-warfare | **Epic**: E2 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The power grid is the lifeline of infrastructure survival. Players must manage power generation, distribution, and backup while facing enemy attacks on grid infrastructure. Blackouts cascade through dependent systems (water, heat, communications), and grid warfare introduces strategic layer where attackers target power nodes.

## Target Users

- Players managing city power infrastructure under crisis
- Mod developers extending grid mechanics
- QA testing blackout cascade logic

## Functional Requirements

- [ ] **FR-PGW-001**: PowerGrid domain tracks generation capacity, load, and distribution topology per grid segment
- [ ] **FR-PGW-002**: Blackout domain detects and propagates power failures; cascading failures affect dependent systems within configurable latency
- [ ] **FR-PGW-003**: PowerBackup domain manages generator reserves, fuel levels, and automatic switchover on grid failure
- [ ] **FR-PGW-004**: GridWarfare domain enables strategic targeting of power infrastructure by threat actors
- [ ] **FR-PGW-005**: Power restoration follows repair priority queue; critical facilities (hospitals, military) get priority
- [ ] **FR-PGW-006**: Grid topology visualization in UI showing live power flow, load balance, and failure points
- [ ] **FR-PGW-007**: Engineering domain coordinates physical repairs of damaged grid infrastructure

## Non-Functional Requirements

- Domains: `PowerGrid/`, `Blackout/`, `PowerBackup/`, `GridWarfare/`, `Engineering/`
- All grid state changes emit events for other domains to react
- Grid topology persisted in save format

## Constraints and Dependencies

- Depends on: ModState (csv-001) for shared state access
- Depends on: ThreatDamage (csv-004) for attack damage values
- Grid calculations must not block main thread; async repair scheduling

## Acceptance Criteria

- [ ] Blackout cascades correctly to dependent systems
- [ ] Backup generators activate within 1 tick of grid failure
- [ ] Grid topology correctly reflects damage and repairs
- [ ] Power flow calculations handle circular topology without infinite loops
- [ ] Save/load preserves grid state including in-progress repairs

## Status

| Story | Status |
|-------|--------|
| E2.1 PowerGrid tracking | Complete |
| E2.2 Blackout cascade | Complete |
| E2.3 PowerBackup switchover | Complete |
| E2.4 GridWarfare targeting | Partial |
| E2.5 Repair priority queue | Complete |
| E2.6 Grid topology UI | Partial |
| E2.7 Engineering repairs | Partial |
