# Command History Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox syntax for tracking.

**Goal:** Persist bounded accepted command IDs across save/load so replay protection survives restoration.

**Architecture:** Encode a versioned command-history record in `journal_checkpoint`; decode it before publishing a loaded runtime. The record has a magic tag, version, count, and sorted 16-byte IDs. It is already protected by the existing canonical save hash and checksum.

**Tech Stack:** Rust 1.89, FlatBuffers 25.12.19, civic-ffi tests.

---

### Task 1: Define failing persistence behavior

**Files:**
- Modify: `native/ffi/src/lib.rs`

- [ ] Add a test that accepts an ID, saves, loads, and rejects that same ID with the restored revision.
- [ ] Run the focused test and observe failure because journal checkpoint currently remains unchanged.

### Task 2: Add bounded checkpoint codec

**Files:**
- Modify: `native/ffi/src/lib.rs`

- [ ] Encode `CSWH`, little-endian version 1, little-endian count, and sorted 16-byte IDs.
- [ ] Reject an invalid tag, version, length, count, or duplicate ID as `CorruptData` before runtime publication.
- [ ] Regenerate checkpoint and canonical/checksum hashes whenever an accepted batch changes history.

### Task 3: Verify and publish

**Files:**
- Modify: `native/README.md`
- Modify: `.agileplus/civic-warfare-program/program-memory.md`

- [ ] Run `cargo test --manifest-path native/Cargo.toml --locked` and the WP02 boundary checks.
- [ ] Document that accepted IDs persist through the checkpoint and publish the commit.
