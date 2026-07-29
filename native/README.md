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

The exact Rust toolchain is pinned in `rust-toolchain.toml`; `Cargo.lock` is
committed even though this first slice has no external crates.
