# Command Batch Atomicity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox syntax for tracking.

**Goal:** Accept only semantically valid command batches and commit command IDs and revision as one deterministic operation.

**Architecture:** Decode an already verified FlatBuffers `CommandBatch` into a temporary list of fixed-width IDs. Validate every command and the whole batch before mutating `Runtime`; only then record accepted IDs and increment revision once. Rejections preserve runtime state.

**Tech Stack:** Rust 1.89, FlatBuffers 25.12.19, civic-ffi unit tests.

---

### Task 1: Prove semantic rejection is missing

**Files:**
- Modify: `native/ffi/src/lib.rs`

- [ ] Write tests for invalid command IDs, in-batch duplicate IDs, and unchanged status following rejection.
- [ ] Run `cargo test --manifest-path native/ffi/Cargo.toml --locked command_batch`; expect failure because schema-valid invalid commands are currently accepted.

### Task 2: Decode and validate a candidate

**Files:**
- Modify: `native/ffi/src/lib.rs:116`

- [ ] Add `MAX_COMMANDS_PER_BATCH = 256`, fixed 16-byte IDs, and `decode_command_batch(bytes, runtime) -> Result<Vec<[u8; 16]>, CswResult>`.
- [ ] Require schema v1; 1..=256 commands; 16-byte command/campaign/issuer IDs; campaign match; non-None kind; non-empty payload; submitted tick not later than scheduled tick; expected revision match; no duplicate IDs within or before the batch.
- [ ] Re-run the focused test; expect pass.

### Task 3: Commit candidate atomically

**Files:**
- Modify: `native/ffi/src/lib.rs:41,339`

- [ ] Add `accepted_command_ids: BTreeSet<[u8; 16]>` to Runtime.
- [ ] Extend the set and increment revision exactly once only after candidate decoding succeeds.
- [ ] Run `cargo test --manifest-path native/Cargo.toml --locked`; expect all native tests to pass.

### Task 4: Record and publish evidence

**Files:**
- Modify: `.agileplus/civic-warfare-program/program-memory.md`
- Modify: `native/README.md`

- [ ] State that this is deterministic boundary bookkeeping, not command gameplay execution.
- [ ] Run `bash tests/wp02/test_native_workspace.sh && bash tests/wp02/test_contract_boundaries.sh`; expect both to pass.
- [ ] Commit and push the focused change.
