# Testing Strategy Index

WP01 public baseline: `bash tests/public-audit/test_contracts_build.sh` verifies that the contracts
project has no private CS2 toolkit import and compiles under `net8.0`. It was recorded red against the
former user-scoped `Mod.props` import, then green after the project boundary was made self-contained.

The installed-game adapter is intentionally excluded from this public test: it requires legally local
CS2 assemblies, the modding toolkit, and omitted private generators. That lane must produce separate
native launch smoke evidence on a licensed host.

The public workflow also runs version/privacy/license/notice/size checks, UI Vitest and lint-rule tests,
declaration typechecking, strict ESLint, and production-only npm audit. The full dev dependency audit is
reported as a remediation artifact because the current lockfile has seven known findings.

WP02-A adds a pinned Rust 1.89 workspace smoke lane: `bash tests/wp02/test_native_workspace.sh`.
It verifies the five-crate inward dependency graph and runs locked unit/doc tests; FlatBuffers and the
final FFI conformance suite remain deliberately pending until `flatc` is pinned.
The companion `bash tests/wp02/test_contract_boundaries.sh` compiles the C
header and rejects platform-dependent status structs, unframed FlatBuffers
roots, and projection schemas without removals, alerts, or explanations.
