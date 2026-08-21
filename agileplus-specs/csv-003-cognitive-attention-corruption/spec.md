---
spec_id: csv-003
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Cognitive Attention Corruption

**Slug**: csv-003-cognitive-attention-corruption | **Epic**: E3 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

Citizens in the mod have cognitive states that affect their behavior. The Cognitive domain models attention, decision-making, and corruption susceptibility. Under prolonged crisis, citizen attention degrades, making them more susceptible to corruption, panic, and poor decisions. The Corruption domain tracks institutional decay.

## Target Users

- Players managing citizen morale and institutional integrity
- Mod developers extending social simulation mechanics

## Functional Requirements

- [ ] **FR-COG-001**: Cognitive domain tracks per-citizen attention span, focus, and decision quality metrics
- [ ] **FR-COG-002**: Attention domain models attention allocation across competing priorities (work, safety, news, social)
- [ ] **FR-COG-003**: Corruption domain tracks institutional corruption levels; corruption spreads through social networks
- [ ] **FR-COG-004**: Corruption with Modernization subsystem: modernization efforts reduce corruption but require resources
- [ ] **FR-COG-005**: Cognitive Ops subsystem manages batch citizen cognitive updates; placement algorithms for cognitive buildings
- [ ] **FR-COG-006**: Cognitive Threats subsystem models disinformation, propaganda, and cognitive warfare effects
- [ ] **FR-COG-007**: Cognitive UI exposes citizen mental state and institutional integrity to player

## Non-Functional Requirements

- Domains: `Cognitive/` (Core, Ops, Placement, Threats, UI), `Attention/`, `Corruption/`
- Cognitive calculations batched per tick to avoid per-entity overhead
- Corruption values use fixed-point to avoid floating-point nondeterminism

## Constraints and Dependencies

- Depends on: ModState (csv-001)
- Depends on: Network (csv-006) for social graph propagation
- Depends on: PowerGrid (csv-002) — power outages degrade cognitive functions

## Acceptance Criteria

- [ ] Citizen attention degrades proportionally to crisis severity
- [ ] Corruption spreads through social connections with configurable rate
- [ ] Modernization efforts measurably reduce corruption over time
- [ ] Cognitive threat effects stack correctly with other stressors
- [ ] UI correctly displays per-citizen and aggregate cognitive state

## Status

| Story | Status |
|-------|--------|
| E3.1 Cognitive tracking | Complete |
| E3.2 Attention allocation | Complete |
| E3.3 Corruption spread | Complete |
| E3.4 Corruption modernization | Complete |
| E3.5 Cognitive ops batching | Complete |
| E3.6 Cognitive threats | Partial |
| E3.7 Cognitive UI | Complete |
