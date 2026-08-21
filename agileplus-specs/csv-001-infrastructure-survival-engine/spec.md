---
spec_id: csv-001
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: Infrastructure Survival Engine

**Slug**: csv-001-infrastructure-survival-engine | **Epic**: E1 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The mod transforms Cities: Skylines II from a city builder into an infrastructure survival game. The core engine must intercept vanilla game loops via Harmony patches, inject crisis-state tracking (blackouts, grid failures, threat damage), and expose a unified ModState that all 29 domains read/write.

## Target Users

- Mod developers extending CivicSurvival domains
- Players experiencing the survival crisis loop
- QA validating cross-domain interactions

## Functional Requirements

- [ ] **FR-ENG-001**: Harmony patch intercept of CS2 game loop at specified hook points; mod state persists across save/load
- [ ] **FR-ENG-002**: Unified ModState singleton accessible from all 29 domains; thread-safe reads, batched writes per tick
- [ ] **FR-ENG-003**: DifficultyPresets system with 5 tiers (Casual, Normal, Veteran, Hardcore, Catastrophic)
- [ ] **FR-ENG-004**: EngineConstants defines timing intervals, audio triggers, and threat parameters
- [ ] **FR-005**: Core component lifecycle: bootstrap, tick, post-tick, unload with guard rails
- [ ] **FR-ENG-006**: CIVIC_PERF instrumentation tracking tick budgets per domain
- [ ] **FR-ENG-007**: Save/load integration: ModState serialized with CS2 save format

## Non-Functional Requirements

- Entry point: `Mod.cs` (668 lines)
- Core layer: `Core/` (Adapters, Attributes, Components, Features, Infrastructure, Interfaces, Systems, Utils)
- Zero native code; pure C# managed runtime
- All patches use Harmony prefix/postfix for forward compatibility

## Constraints and Dependencies

- Depends on: Colossal Order assemblies via `$(GameManagedPath)`
- Depends on: Lib.Harmony 2.2.2 for runtime patching
- No BepInEx dependency (uses Paradox Mods loader)
- Must not conflict with vanilla CS2 save format

## Acceptance Criteria

- [ ] Mod loads without errors on CS2 v1.6.x
- [ ] All 5 difficulty presets apply correctly
- [ ] Save/load round-trips preserve mod state
- [ ] CIVIC_PERF reports tick budgets for all active domains
- [ ] Unload cleans up all Harmony patches

## Status

| Story | Status |
|-------|--------|
| E1.1 Harmony patch framework | Complete |
| E1.2 ModState singleton | Complete |
| E1.3 DifficultyPresets | Complete |
| E1.4 EngineConstants | Complete |
| E1.5 Core component lifecycle | Complete |
| E1.6 CIVIC_PERF instrumentation | Partial |
| E1.7 Save/load integration | Partial |
