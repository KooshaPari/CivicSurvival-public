---
spec_id: csv-006
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Diplomacy Intel Mobilization

**Slug**: csv-006-diplomacy-intel-mobilization | **Epic**: E6 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

External relations, intelligence gathering, and military mobilization form the strategic layer. Players negotiate with neighbors, conduct espionage, manage refugee flows, and mobilize military forces. NeighborEnvy models diplomatic pressure from adjacent cities.

## Target Users

- Players managing international relations
- Mod developers extending diplomacy or military mechanics

## Functional Requirements

- [ ] **FR-DIP-001**: Diplomacy domain manages treaties, alliances, trade agreements, and diplomatic standing
- [ ] **FR-DIP-002**: Intel domain provides espionage, counter-intelligence, and threat assessment from foreign actors
- [ ] **FR-DIP-003**: Mobilization domain manages military recruitment, deployment, and readiness states
- [ ] **FR-DIP-004**: NeighborEnvy models diplomatic pressure and resource competition from adjacent cities
- [ ] **FR-DIP-005**: Refugees domain handles displaced population flows from conflict zones
- [ ] **FR-DIP-006**: Diplomacy integrates with GridWarfare for coordinated infrastructure attacks
- [ ] **FR-DIP-007**: Diplomacy UI exposes foreign relations status and negotiation interface

## Non-Functional Requirements

- Domains: `Diplomacy/`, `Intel/`, `Mobilization/`, `NeighborEnvy/`, `Refugees/`
- Diplomatic AI decisions must be deterministic for replay
- Refugee calculations batched per tick

## Constraints and Dependencies

- Depends on: ModState (csv-001)
- Depends on: Economics (csv-005) — trade agreements affect economy
- Depends on: ThreatPipeline (csv-004) — military readiness affects threat response

## Acceptance Criteria

- [ ] Treaty negotiations produce deterministic outcomes for same inputs
- [ ] Intel operations have configurable success/failure probabilities
- [ ] Military mobilization correctly scales with population and resources
- [ ] Refugee flows integrate with housing and social services
- [ ] Diplomacy UI clearly shows relationship status and options

## Status

| Story | Status |
|-------|--------|
| E6.1 Diplomacy treaties | Complete |
| E6.2 Intel operations | Partial |
| E6.3 Mobilization management | Complete |
| E6.4 NeighborEnvy modeling | Complete |
| E6.5 Refugee handling | Partial |
| E6.6 GridWarfare integration | Partial |
| E6.7 Diplomacy UI | Complete |
