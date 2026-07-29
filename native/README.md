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
golden malformed-buffer vectors are the next gate.

The exact Rust toolchain is pinned in `rust-toolchain.toml`; `Cargo.lock` is
committed even though this first slice has no external crates.
