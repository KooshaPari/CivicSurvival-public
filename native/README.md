# Native WP02-A boundary

This workspace is the host-independent foundation for the future warfare runtime.

```text
model <- rules <- application <- ffi
                              \-> headless
```

The dependency direction is intentional: domain data is inward, application
orchestration depends on rules, and FFI/headless surfaces remain outer adapters.
No combat, economy, Unity, or network behavior belongs here until the ABI and
schema conformance gates are green.

The contract artifacts are deliberately stricter than a convenient FFI:
status is serialized through `csw_status_into` rather than a C struct,
FlatBuffers messages are framed by an `Envelope`/`RootPayload` union, and
projection deltas carry explicit removals, alerts, and explanations. The
static boundary test catches regressions while pinned `flatc` conformance is
still a WP02 follow-up.

`civic-ffi` now builds as `cdylib`/`rlib` and exposes a no-op, panic-contained
transport lifecycle: create/load/destroy, bounded step/submit calls, and
caller-owned status/error/poll/save buffers. It intentionally does not parse
FlatBuffers or claim gameplay behavior; generated verifier integration and
golden malformed-buffer vectors are the next gate. The C11 fixture at
`tests/wp02/ffi_smoke.c` proves that the exported library links and executes;
load/submit/poll/save are still intentionally non-authoritative stubs.
CI also generates Rust bindings with the pinned FlatBuffers runtime and runs
valid/truncated/bad-identifier verifier vectors before this FFI is allowed to
decode payloads. Building `civic-ffi` locally now requires `flatc` 25.12.19
on `PATH` (or `CIVIC_FLATC=/path/to/flatc`); this is intentional so the FFI
cannot silently compile against stale generated bindings.

Transport typing is explicit: load requires a `SaveEnvelope`, command
submission requires a `CommandBatch`, and generic construction may use an
empty bootstrap buffer or any structurally valid envelope. Payload decoding,
state replacement, and output serialization remain future slices.

The exact Rust toolchain is pinned in `rust-toolchain.toml`; `Cargo.lock` is
committed even though this first slice has no external crates.
