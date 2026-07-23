---
work_package_id: WP20
title: Document architecture, contracts, mod build, nativ (WP20)
feature: Civic Warfare and Resilient City Program
feature_slug: civic-warfare-program
sequence: 20
state: planned
created_at: 2026-07-22T00:00:00Z
---

# Work Package: Document architecture, contracts, mod build, nativ (WP20)

## Feature
Civic Warfare and Resilient City Program (`civic-warfare-program`)

## Acceptance Criteria
- FR-096 -- Document architecture, contracts, mod build, native toolchain, scenario authoring, balancing, testing, debugging, privacy, security, accessibility, and player mechanics from the implementation truth.
- FR-097 -- Maintain one canonical version across project, manifest, UI, schemas, ABI, save, rules, release notes, and packaged artifacts.
- FR-098 -- Pin dependencies and toolchains, record SPDX provenance and modifications, and require an ADR plus full compatibility review before importing copyleft code or relicensing the project.
- FR-099 -- Package and smoke-test the Windows x64 native library, schemas, C# host, UI bundle, content packs, notices, licenses, and recovery behavior from a clean release environment.
- FR-100 -- Ship only after every FR has linked evidence, every work package is done, governance validation passes, audit chain verifies, documentation matches behavior, and rollback is a package-level version restore rather than runtime compatibility code.
- FR-120 -- Produce a signed release dossier containing provenance, SBOM, licenses, reproducible hashes, test/performance evidence, privacy review, accessibility review, known issues, and recovery instructions.

## Instructions
Implement this work package according to the acceptance criteria above and the canonical dependency, ownership, evidence, estimate, and validation contract in `.agileplus/civic-warfare-program/tasks.md` and `plan.md`.
Refer to `.agileplus/civic-warfare-program/spec.md` for the full specification and
`.agileplus/civic-warfare-program/plan.md` for the implementation plan.