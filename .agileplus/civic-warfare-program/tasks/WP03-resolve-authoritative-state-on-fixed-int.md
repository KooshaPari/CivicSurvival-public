---
work_package_id: WP03
title: Resolve authoritative state on fixed integer ticks (WP03)
feature: Civic Warfare and Resilient City Program
feature_slug: civic-warfare-program
sequence: 3
state: planned
created_at: 2026-07-22T00:00:00Z
---

# Work Package: Resolve authoritative state on fixed integer ticks (WP03)

## Feature

Civic Warfare and Resilient City Program (`civic-warfare-program`)

## Acceptance Criteria

- FR-011 -- Resolve authoritative state on fixed integer ticks using fixed-point domain newtypes, stable IDs, stable iteration, explicit tie-breaking, and named deterministic random streams.
- FR-012 -- Implement single-writer staged ticks: ingest observations, validate commands, plan, resolve economy/logistics, resolve operations/combat, apply consequences, then project.
- FR-013 -- Persist versioned snapshots plus append-only player/AI commands and coarse outcomes, with periodic checkpoints, compaction, PRNG version, and canonical BLAKE3 hashes.
- FR-014 -- Provide headless record/replay, golden replay, cross-build hash comparison, desync localization, and deterministic debug traces.
- FR-015 -- Use deterministic parallelism only for read-only scoring or tiles, stable-sort results, and commit mutation serially.
- FR-103 -- Maintain golden vectors for fixed-point arithmetic, random-stream derivation, canonical serialization, state hashing, journal replay, and snapshot restore.

## Instructions

Implement this work package according to the acceptance criteria above and the canonical dependency, ownership, evidence, estimate, and validation contract in `.agileplus/civic-warfare-program/tasks.md` and `plan.md`.
Refer to `.agileplus/civic-warfare-program/spec.md` for the full specification and
`.agileplus/civic-warfare-program/plan.md` for the implementation plan.
