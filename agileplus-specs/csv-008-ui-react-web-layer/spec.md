---
spec_id: csv-008
state: ACTIVE
plan_status: IN_PROGRESS
last_audit: 2026-08-19
---

# Specification: UI React Web Layer

**Slug**: csv-008-ui-react-web-layer | **Epic**: E8 | **Date**: 2026-08-19 | **State**: ACTIVE

## Problem Statement

The mod provides a comprehensive React/TypeScript UI layer rendered through Coherent GameFace. The UI must display 29 domains of game state, provide interactive controls, and maintain performance under rapid state updates. The UI layer includes custom ESLint rules for CS2-specific patterns.

## Target Users

- Players interacting with mod UI panels
- UI developers extending mod interface
- QA testing UI responsiveness and correctness

## Functional Requirements

- [ ] **FR-UI-001**: React 18 UI renders domain-specific panels (grid status, threat tracking, economy charts, diplomacy map)
- [ ] **FR-UI-002**: Coherent GameFace bridge for bidirectional C#/TypeScript communication
- [ ] **FR-UI-003**: Webpack build pipeline producing optimized bundles for CS2 mod loading
- [ ] **FR-UI-004**: Custom ESLint rules enforce CS2-specific patterns (no DOM access, Coherent API usage)
- [ ] **FR-UI-005**: Theme system supports light/dark modes and accessibility settings
- [ ] **FR-UI-006**: Performance: UI updates batched to avoid frame drops during rapid state changes
- [ ] **FR-UI-007**: TypeScript strict mode with comprehensive type coverage for mod API contracts

## Non-Functional Requirements

- UI source: `CivicSurvival/UI/` (212 TypeScript files, 180KB JS)
- Custom ESLint: `UI/eslint-rules/` (10 CS2-specific rules)
- Tests: `UI/tests/` (10 vitest test files)
- Build: Webpack 5 with code splitting

## Constraints and Dependencies

- Depends on: Coherent GameFace runtime (CS2 embedded browser)
- Depends on: C# mod API contracts for data flow
- No access to browser DOM APIs (Coherent sandbox)

## Acceptance Criteria

- [ ] All domain panels render without errors
- [ ] TypeScript compilation passes with zero errors
- [ ] ESLint passes with zero violations
- [ ] 10 UI tests pass
- [ ] Build produces optimized bundle under 500KB

## Status

| Story | Status |
|-------|--------|
| E8.1 React component framework | Complete |
| E8.2 Coherent bridge | Complete |
| E8.3 Webpack pipeline | Complete |
| E8.4 Custom ESLint rules | Complete |
| E8.5 Theme system | Partial |
| E8.6 Performance batching | Complete |
| E8.7 TypeScript strict | Complete |
