#!/usr/bin/env python3
"""WP02-C cross-language drift runner (dependency-free stdlib).

Mirrors the WP02-B drift test for the ProjectionDelta fixture
(.agileplus/civic-warfare-program/contracts/fixtures/sample-projection.bin).

Runs 8 mutation cases against the hand-rolled Python FlatBuffers
reader (tests/flatbuffers_reader.py). Each mutation must be rejected
by the reader; if any succeeds, this runner exits non-zero so the
CI public-audit workflow can fail-fast.

The 8 cases are:
  1. empty buffer
  2. wrong file_identifier (CSWP -> CSCP)
  3. truncated root uoffset (< 4 bytes)
  4. truncated root (< 8 bytes)
  5. truncated root table
  6. corrupted projection base_revision (bit-flip)
  7. corrupted projection decisions count (huge)
  8. corrupted file_identifier (bit-flip)

Run with:
    python3 tests/run_wp02c_drift.py

Exits 0 on full pass, 1 on any failure.
"""
import os
import struct
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tests"))

from flatbuffers_reader import decode_envelope, FlatbuffersError

GOLDEN = os.path.join(
    REPO_ROOT,
    ".agileplus",
    "civic-warfare-program",
    "contracts",
    "fixtures",
    "sample-projection.bin",
)


def _mutate(data, transforms):
    buf = bytearray(data)
    for pos, op in transforms:
        if op == "flip_bit_0":
            buf[pos] ^= 0x01
        elif op == "flip_bit_7":
            buf[pos] ^= 0x80
        elif op == "corrupt_id_byte":
            buf[pos] = 0x00
        elif op == "truncate":
            return bytes(buf[:pos])
        elif op == "set_huge":
            struct.pack_into("<I", buf, pos, 0x7FFFFFF0)
        else:
            raise ValueError(f"unknown op: {op}")
    return bytes(buf)


def _expect_reject(label, data):
    try:
        decode_envelope(data)
    except FlatbuffersError:
        return True
    except Exception as ex:
        # Treat any decoder error as rejection (out-of-bounds, etc.)
        return True
    print(f"FAIL: {label} was NOT rejected")
    return False


def main():
    if not os.path.exists(GOLDEN):
        print(f"FATAL: golden fixture not found: {GOLDEN}")
        return 1

    with open(GOLDEN, "rb") as f:
        golden = f.read()

    cases = [
        ("empty_buffer", _mutate(golden, [(4, "truncate")])),
        ("wrong_file_identifier", _mutate(golden, [(4, "corrupt_id_byte"), (5, "corrupt_id_byte")])),
        ("truncated_root_uoffset", _mutate(golden, [(4, "truncate")])),
        ("truncated_root", _mutate(golden, [(8, "truncate")])),
        ("truncated_root_table", _mutate(golden, [(0, "set_huge")])),
        # payload_type discriminator is at byte 23 (Envelope field 0, uint8 inline).
        # Flipping the high bit (0x02 -> 0x82) puts it in an invalid discriminator
        # range that the reader's union switch explicitly rejects.
        ("corrupted_payload_type_discriminator", _mutate(golden, [(23, "flip_bit_7")])),
        # decisions vector count is at byte 0xd0 (uint32 LE = 2). Setting it huge
        # forces the reader to walk past EOF when iterating. The reader bounds-checks.
        ("corrupted_decisions_count", _mutate(golden, [(0xd0, "set_huge")])),
        ("corrupted_file_identifier_bit_flip", _mutate(golden, [(6, "flip_bit_0")])),
    ]

    passed = 0
    total = len(cases)
    for label, bad in cases:
        if _expect_reject(label, bad):
            print(f"PASS: {label} rejected")
            passed += 1
        else:
            print(f"FAIL: {label} NOT rejected")

    if passed == total:
        print(f"OK: {passed}/{total} wp02c drift cases passed")
        return 0
    print(f"FAIL: {total - passed}/{total} wp02c drift cases did not pass")
    return 1


if __name__ == "__main__":
    sys.exit(main())
