# WP02-A Provenance Audit

**Audit date:** 2026-08-30  
**Current public baseline:** `1a7a229bb2eccb04c0d91ad3c9d35ab93443f258`  
**Provenance source:** `origin/feat/civic-warfare-program` at
`3bd4431b083101669fc9244e2e09afe182c2b10b`

## Purpose

This record separates the historical native prototype from admissible current
implementation work. It is an audit and reuse map, not authorization to merge
production warfare behavior before WP01 is accepted.

## Reuse map

| WP02 requirement                       | Historical evidence                                                     | Status    | Required successor proof                                                                         |
| -------------------------------------- | ----------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------ |
| Rust workspace and inward dependencies | `native/Cargo.toml`, `model`, `rules`, `application`, `ffi`, `headless` | candidate | clean checkout build with pinned Rust toolchain; architecture test                               |
| ABI version/errors/opaque handles      | `native/ffi/src/lib.rs`, `native/ffi/src/tests.rs`                      | candidate | C11 lifecycle smoke, invalid-handle tests, ABI handshake                                         |
| FlatBuffers toolchain                  | `native/rust-toolchain.toml`, `native/flatbuffers-toolchain.toml`       | candidate | pinned `flatc` installation, generated Rust/C#/TS/Python outputs, valid/truncated/bad-ID vectors |
| Deterministic command boundary         | `native/ffi/src/command.rs` and historical tests                        | candidate | ordering, deduplication, revision, campaign, and failure golden vectors                          |
| Save/load integrity                    | historical FFI save tests and `CSWH` framing                            | candidate | transactional load, tamper rejection, bounded allocation, byte-stable round trip                 |
| Projection delivery                    | `native/ffi/src/projection.rs`                                          | candidate | caller-owned `poll_into`, required-length behavior, repeatable current snapshot semantics        |
| Gameplay behavior                      | none claimed by prototype                                               | absent    | separate post-WP01 domain work packages                                                          |

## Explicit exclusions

- `native/target/**` and generated build output are not source evidence.
- Historical code is not copied wholesale into `main`.
- No Unity, CS2, filesystem, network, wall-clock, or UI dependency may enter
  the domain crates.
- No ground, air, naval, invasion, economy, or AI behavior is implied by this
  boundary spike.

## Entry and exit gates

WP02-A may be prepared as documentation, schemas, tests, and isolated tooling
before WP01. A successor implementation PR may merge only after:

1. WP01 licensed-host build, launch-smoke, artifact-hash, provenance, and
   supported AgilePlus evidence are accepted.
2. `flatc` and Rust toolchain versions are reproducibly installed.
3. ABI, schema, lifecycle, persistence, projection, and architecture tests
   pass on a clean checkout.
4. The successor diff excludes generated/build output and records every
   borrowed file and license decision.

Until then, this document is a machine-readable planning and provenance aid;
it does not change the production implementation gate.
