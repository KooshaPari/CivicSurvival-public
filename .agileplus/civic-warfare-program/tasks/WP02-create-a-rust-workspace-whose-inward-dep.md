---
work_package_id: WP02
title: Create a Rust workspace whose inward dependency di (WP02)
feature: Civic Warfare and Resilient City Program
feature_slug: civic-warfare-program
sequence: 2
state: planned
created_at: 2026-07-22T00:00:00Z
---

# Work Package: Create a Rust workspace whose inward dependency di (WP02)

## Feature

Civic Warfare and Resilient City Program (`civic-warfare-program`)

## Acceptance Criteria

- FR-006 -- Create a Rust workspace whose inward dependency direction separates model, rules, geography, statecraft, economy, logistics, forces, operations, combat, AI, replay, FFI, and headless runner.
- FR-007 -- Generate a versioned C ABI and C# bindings with opaque handles, caller-owned buffers, explicit error enums, ABI handshake, panic containment, and fail-closed warfare disablement.
- FR-008 -- Define one pinned FlatBuffers schema toolchain that generates Rust, C#, TypeScript, and Python command, outcome, projection, rules, and save envelopes with conformance checks.
- FR-009 -- Generalize the existing durable intent-resolution-signal pattern into idempotent ordered commands, exactly-once outcomes, and ephemeral projection signals.
- FR-010 -- Enforce bounded-context and namespace/crate dependency rules through architecture tests; prohibit Unity, filesystem, wall-clock, networking, and UI dependencies inside the Rust domain kernel.
- FR-102 -- Record and test every public boundary's ownership, lifecycle, versioning, batching, allocation, failure, and compatibility policy before dependent lanes begin.

## Instructions

Implement this work package according to the acceptance criteria above and the canonical dependency, ownership, evidence, estimate, and validation contract in `.agileplus/civic-warfare-program/tasks.md` and `plan.md`.
Refer to `.agileplus/civic-warfare-program/spec.md` for the full specification and
`.agileplus/civic-warfare-program/plan.md` for the implementation plan.
