---
spec_id: csv-005
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Economics Finance Shadow Economy

**Slug**: csv-005-economics-finance-shadow | **Epic**: E5 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The mod introduces economic survival mechanics. Players manage budgets, taxation, trade sanctions, and resource allocation while facing economic warfare. The Shadow Economy domain models black markets, smuggling, and corruption-driven economic channels that emerge when legitimate economy fails.

## Functional Requirements

- [ ] **FR-ECO-001**: Economics domain tracks GDP, employment, trade balance, and resource availability
- [ ] **FR-ECO-002**: Finance domain manages budgets, taxation rates, bonds, and international aid
- [ ] **FR-ECO-003**: ShadowEconomy domain models black market activity, smuggling routes, and corruption-driven trade
- [ ] **FR-ECO-004**: Economics responds to infrastructure failures (power outages reduce productivity, blackouts halt trade)
- [ ] **FR-ECO-005**: Finance integrates with Diplomacy for trade agreements, sanctions, and economic warfare
- [ ] **FR-ECO-006**: Shadow economy grows as legitimate economy weakens; player can choose to suppress or co-opt
- [ ] **FR-ECO-007**: Economic indicators exposed through UI with historical trend charts

## Non-Functional Requirements

- Domains: `Economics/`, `Finance/`, `ShadowEconomy/`
- Economic calculations must be deterministic for replay
- Financial state persisted in save format with version migration

## Constraints and Dependencies

- Depends on: ModState (csv-001)
- Depends on: PowerGrid (csv-002) — economic activity requires infrastructure
- Depends on: Diplomacy (csv-006) — trade agreements affect economy

## Acceptance Criteria

- [ ] GDP correctly reflects infrastructure state and crisis level
- [ ] Tax rate changes propagate to citizen satisfaction and revenue
- [ ] Shadow economy grows/shrinks based on legitimate economy health
- [ ] Financial state survives save/load round-trips
- [ ] Economic UI charts update in real-time

## Status

| Story | Status |
|-------|--------|
| E5.1 Economics tracking | Complete |
| E5.2 Finance management | Complete |
| E5.3 ShadowEconomy modeling | Complete |
| E5.4 Infrastructure coupling | Complete |
| E5.5 Diplomacy integration | Partial |
| E5.6 Shadow economy dynamics | Complete |
| E5.7 Economic UI | Partial |
