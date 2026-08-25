---
work_package_id: WP19
title: Add unit, property, contract, integration, replay, (WP19)
feature: Civic Warfare and Resilient City Program
feature_slug: civic-warfare-program
sequence: 19
state: planned
created_at: 2026-07-22T00:00:00Z
---

# Work Package: Add unit, property, contract, integration, replay, (WP19)

## Feature
Civic Warfare and Resilient City Program (`civic-warfare-program`)

## Acceptance Criteria
- FR-091 -- Add unit, property, contract, integration, replay, fuzz, mutation, UI, accessibility, localization, native smoke, scenario, performance, and soak suites tied to requirement evidence.
- FR-092 -- Prove deterministic replay through identical hashes for repeated 10,000-tick runs across debug/release and supported Windows x64 build configurations.
- FR-093 -- Enforce target-scale budgets: normal Rust tick p95 at most 5 ms, planning tick p95 at most 25 ms, C# bridge p95 at most 1 ms, and zero steady-state managed allocation on poll/render paths.
- FR-094 -- Fuzz every ABI/schema/save decoder, reject corrupt or incompatible inputs without undefined behavior, contain Rust panics, and disable warfare without crashing the city simulation.
- FR-095 -- Produce structured performance counters, replay/desync diagnostics, AI decision traces, supply causal traces, privacy-safe errors, SBOM, licenses, and dependency vulnerability reports.
- FR-119 -- Make the complete validation suite emit machine-readable FR-to-test-to-evidence records consumable by AgilePlus governance and release gates.

## Instructions
Implement this work package according to the acceptance criteria above and the canonical dependency, ownership, evidence, estimate, and validation contract in `.agileplus/civic-warfare-program/tasks.md` and `plan.md`.
Refer to `.agileplus/civic-warfare-program/spec.md` for the full specification and
`.agileplus/civic-warfare-program/plan.md` for the implementation plan.