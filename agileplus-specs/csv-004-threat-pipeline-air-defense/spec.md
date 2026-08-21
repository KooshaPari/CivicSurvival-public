---
spec_id: csv-004
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Threat Pipeline and Air Defense

**Slug**: csv-004-threat-pipeline-air-defense | **Epic**: E4 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The threat pipeline is the core crisis driver. Threats (missiles, drones, cyber attacks, ground incursions) originate from ThreatFlight, are detected by Spotters/Intel, engage through AirDefense, deal damage via ThreatDamage, and display through ThreatUI. Countermeasures provide defensive responses.

## Target Users

- Players responding to active threats
- Mod developers extending threat types
- QA validating threat engagement math

## Functional Requirements

- [ ] **FR-THR-001**: ThreatFlight domain manages threat trajectory, speed, and targeting; threats follow physics-based paths
- [ ] **FR-THR-002**: Spotters domain detects incoming threats at configurable ranges; detection probability based on weather/time/technology
- [ ] **FR-THR-003**: Intel domain provides threat assessment, origin identification, and early warning
- [ ] **FR-THR-004**: AirDefense domain manages SAM sites, interceptors, CIWS; engagement rules and probability of kill
- [ ] **FR-THR-005**: Countermeasures domain provides jamming, decoys, hardening; countermeasure effectiveness degrades with use
- [ ] **FR-THR-006**: ThreatDamage domain calculates impact damage, collateral effects, and infrastructure degradation
- [ ] **FR-THR-007**: ThreatUI domain renders real-time threat tracking, radar displays, and engagement status

## Non-Functional Requirements

- Domains: `ThreatFlight/`, `Spotters/`, `Intel/`, `AirDefense/`, `Countermeasures/`, `ThreatDamage/`, `ThreatUI/`
- Threat pipeline must complete within tick budget; early-exit for no-threat ticks
- All threat calculations deterministic for replay compatibility

## Constraints and Dependencies

- Depends on: ModState (csv-001)
- Depends on: PowerGrid (csv-002) — air defense requires power
- Depends on: Waves (csv-004) — threat wave scheduling

## Acceptance Criteria

- [ ] Threats follow deterministic trajectories given same seed
- [ ] Detection probability correctly factors weather, range, and tech level
- [ ] Air defense engagement produces consistent kill/miss outcomes
- [ ] Damage calculations correctly cascade to infrastructure
- [ ] UI renders threat state without frame drops

## Status

| Story | Status |
|-------|--------|
| E4.1 ThreatFlight trajectory | Complete |
| E4.2 Spotters detection | Complete |
| E4.3 Intel assessment | Complete |
| E4.4 AirDefense engagement | Complete |
| E4.5 Countermeasures | Partial |
| E4.6 ThreatDamage calculation | Complete |
| E4.7 ThreatUI rendering | Complete |
