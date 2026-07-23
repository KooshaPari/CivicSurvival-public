# Testing Strategy Index

WP01 public baseline: `bash tests/public-audit/test_contracts_build.sh` verifies that the contracts
project has no private CS2 toolkit import and compiles under `net8.0`. It was recorded red against the
former user-scoped `Mod.props` import, then green after the project boundary was made self-contained.

The installed-game adapter is intentionally excluded from this public test: it requires legally local
CS2 assemblies, the modding toolkit, and omitted private generators. That lane must produce separate
native launch smoke evidence on a licensed host.
