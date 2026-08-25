# Civic ABI v2 Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development or an equivalent independent implementation plus specification and code-quality review. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the preserved native ABI prototype into a bounded, reviewable foundation with safe opaque handles, observable failures, saveable command-history limits, and a defined projection contract.

**Architecture:** Successor branches derive from `origin/main`; `feat/civic-warfare-program` remains immutable evidence. Native ABI v2 uses synchronized, registry-owned `Runtime` values. An exported `CswRuntime *` is a non-null opaque token used only as a registry key; no FFI function dereferences it. `csw_destroy(CswRuntime **)` clears the caller slot and removes that key. All later use of that token returns `InvalidHandle`.

**Tech Stack:** Rust 2024, `std::sync::{Mutex, OnceLock}`, FlatBuffers, C ABI smoke harness, .NET 8 public audit runner.

---

## PR partition

| PR | Base | Allowed paths | Completion proof |
|---|---|---|---|
| `docs(civic): preserve warfare program specification` | `origin/main` | `.agileplus/civic-warfare-program/**`, `docs/sessions/20260722-civic-warfare-program/**` | no generated output; clean diff; reviewable 47-file documentation change |
| `fix(audit): harden public audit execution` | `origin/main` | public-audit workflow, runner, CI script, public-audit tests, required contracts config | .NET 8 target pack, bounded child wait, controlled malformed-JSON failure |
| `feat(native): establish safe ABI v2 handles` | latest merged audit/spec base | `native/**`, `tests/wp02/**`, required ABI contracts | Rust and C lifecycle, error, persistence, and projection tests |

`native/target/**`, UI/localization, manifest/privacy, package-lock, and unrelated historical files are prohibited from these PRs.

## Task 1: Preserve reviewed program artifacts

**Files:** Add `.agileplus/civic-warfare-program/**` and `docs/sessions/20260722-civic-warfare-program/**`.

- [ ] Verify base and preservation source:

  Run: `git rev-parse origin/main origin/feat/civic-warfare-program`

- [ ] Stage only the two allowed documentation trees and reject generated paths:

  Run: `git diff --cached --name-only | rg '^native/target/' && exit 1 || true`

- [ ] Run `git diff --cached --check`; commit `docs(civic): preserve warfare program specification`.

## Task 2: Harden public-audit execution

**Files:** Modify `.github/workflows/public-audit.yml`, `CivicSurvival.PublicAudit/Program.cs`, `scripts/ci/check-public-audit.mjs`, and `tests/public-audit/test_runner.sh`.

- [ ] RED: add a malformed-JSON case to `test_runner.sh`; run `bash tests/public-audit/test_runner.sh malformed-json` and observe the unhandled parser failure.
- [ ] RED: add `--self-test-timeout` to the audit runner test harness; run `dotnet run --project CivicSurvival.PublicAudit -- --self-test-timeout` and observe unbounded wait behavior.
- [ ] GREEN: catch JSON parsing errors and return a stable nonzero diagnostic; use `WaitForExit(TimeSpan)` and terminate only the runner-owned child on timeout; install .NET 8 SDK in the workflow before building `net8.0` projects.
- [ ] Verify: `bash tests/public-audit/test_contracts_build.sh && bash tests/public-audit/test_runner.sh`.
- [ ] Commit only those paths as `fix(audit): harden public audit execution`.

## Task 3: Establish safe ABI v2 handle ownership

**Files:** Modify `native/ffi/src/lib.rs`, `native/ffi/src/tests.rs`, `.agileplus/civic-warfare-program/contracts/civic_warfare.h`, `tests/wp02/ffi_smoke.c`, and `tests/wp02/test_ffi_abi.sh`.

- [ ] RED: add and run four isolated tests:

  - `destroy_clears_the_callers_handle_and_a_repeat_destroy_is_a_noop`;
  - `copied_handle_is_invalid_after_destroy`;
  - `unknown_handle_returns_invalid_handle_without_unsafe_dereference`;
  - `failed_submit_populates_last_error_for_the_live_handle`.

  Run: `cargo test --manifest-path native/Cargo.toml --locked ffi::tests::destroy_clears_the_callers_handle_and_a_repeat_destroy_is_a_noop`

  Expected: fail because current code casts and drops a foreign pointer and never records `last_error`.

- [ ] GREEN: replace `runtime_ref` and `Box::from_raw` with `OnceLock<Mutex<HandleRegistry>>`; allocate monotonically nonzero token IDs, use them only as lookup keys, and return `InvalidHandle` for zero/unknown/destroyed handles. Set `ABI_VERSION` to `2`; change destroy to `void csw_destroy(CswRuntime **)` and write null to its argument slot before return. Record bounded UTF-8 failure diagnostics on live runtimes.
- [ ] Verify: `cargo test --manifest-path native/Cargo.toml --locked && bash tests/wp02/test_ffi_abi.sh`.
- [ ] Commit as `feat(native): establish safe ABI v2 handles`.

## Task 4: Bound persistence and define projection delivery

**Files:** Modify `native/ffi/src/lib.rs`, `native/ffi/src/projection.rs`, `native/ffi/src/tests.rs`, `.agileplus/civic-warfare-program/contracts/warfare.fbs`, `.agileplus/civic-warfare-program/contracts/civic_warfare.h`, and `tests/wp02/test_contract_boundaries.sh`.

- [ ] RED: prove exactly `MAX_ACCEPTED_COMMAND_IDS` unique IDs persist/load and the next ID returns `BudgetExceeded` without changing revision, accepted IDs, or save bytes.
- [ ] RED: prove `csw_poll_into` is a repeatable current-revision snapshot, not an acknowledged event stream; the next mutation replaces its decision list.
- [ ] GREEN: check capacity before extending accepted IDs, record its error, and document the snapshot semantics in the FlatBuffers and public ABI contracts.
- [ ] Verify: `cargo test --manifest-path native/Cargo.toml --locked && bash tests/wp02/test_native_workspace.sh && bash tests/wp02/test_contract_boundaries.sh && bash tests/wp02/test_ffi_abi.sh`.
- [ ] Commit as `fix(native): bound command history and define projections`.

## Task 5: Evidence and WP01 boundary

- [ ] Independently review each successor first for specification compliance and then for code quality; test-fix every actionable finding.
- [ ] Push, open focused PRs, and record SHA, changed-file count, named CI conclusion, review result, and command-output digest.
- [ ] Keep WP01 closed until a licensed Cities: Skylines II adapter produces build, launch-smoke, artifact-hash, and provenance evidence. Public checks alone are insufficient.

## Self-review record

- Scope is partitioned by documentation, audit runner, and native safety; no build output or unrelated product history is bundled.
- Every behavioral repair begins with a named failing test and ends with an exact command matrix.
- No successor is called merge-ready without fresh hosted CI and review proof.
