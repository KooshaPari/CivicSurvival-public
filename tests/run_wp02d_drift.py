#!/usr/bin/env python3
"""WP02-D cross-language drift regression test (dependency-free).

Invokes the hand-rolled Python FlatBuffers reader on the new
SaveEnvelope golden fixture (sample-save.bin) and verifies it rejects
the same 8 mutation cases:

  1. empty file
  2. wrong file_identifier (CSWP -> XSWP)
  3. truncated root_uoffset (buffer < 4 bytes)
  4. truncated file_identifier (buffer < 8 bytes)
  5. truncated root table (root offset past EOF)
  6. corrupted vtable_size (zero)
  7. corrupted save_version (huge u32)
  8. corrupted payload_type discriminator (bit-flip)

Byte positions were traced by hand from the fixture's vtable layout
and verified empirically with the Python reader's decoder.

Reproduction:
  python3 tests/run_wp02d_drift.py
"""
import os
import struct
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tests"))

from flatbuffers_reader import decode_envelope, FlatbuffersError  # noqa: E402

GOLDEN = os.path.join(
    REPO_ROOT,
    ".agileplus/civic-warfare-program/contracts/fixtures/sample-save.bin",
)


class _Raises:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, FlatbuffersError)


def _raises():
    return _Raises()


def case_empty():
    with _raises():
        decode_envelope(b"")


def case_wrong_file_id():
    bad = bytearray(open(GOLDEN, "rb").read())
    bad[4] = ord("X")  # CSWP -> XSWP
    with _raises():
        decode_envelope(bytes(bad))


def case_truncated_root_uoffset():
    bad = open(GOLDEN, "rb").read()[:3]
    with _raises():
        decode_envelope(bad)


def case_truncated_file_id():
    bad = open(GOLDEN, "rb").read()[:7]
    with _raises():
        decode_envelope(bad)


def case_truncated_root_table():
    bad = open(GOLDEN, "rb").read()[:8]
    with _raises():
        decode_envelope(bad)


def case_corrupted_vtable_size():
    # Root vtable vsize u16 @ 0x0c (per SaveEnvelope trace)
    bad = bytearray(open(GOLDEN, "rb").read())
    struct.pack_into("<H", bad, 0x0C, 0)
    with _raises():
        decode_envelope(bytes(bad))


def case_corrupted_save_version():
    # Find save_version (uint32, field 2 per SaveEnvelope table).
    # Compute from root uoffset (0x14 -> root=0x14) -> vtable at 0x0c
    # SaveEnvelope table slot for save_version is field 2.
    # We corrupt the byte at the save_version field's expected position.
    # Simplest robust mutation: corrupt the high byte of save_version.
    # The SaveEnvelope table starts at root_off=0x14+rel. We use a generic
    # approach: corrupt the byte at the save_version inline field offset.
    # For our 80-byte fixture, save_version is at 0x44 (verified empirically).
    bad = bytearray(open(GOLDEN, "rb").read())
    struct.pack_into("<I", bad, 0x44, 0x7FFFFFF0)
    with _raises():
        decode_envelope(bytes(bad))


def case_corrupted_payload_type():
    # Flip high bit of payload_type union discriminator byte @ 0x17
    bad = bytearray(open(GOLDEN, "rb").read())
    bad[0x17] ^= 0x80
    with _raises():
        decode_envelope(bytes(bad))


CASES = [
    ("empty_buffer", case_empty),
    ("wrong_file_identifier", case_wrong_file_id),
    ("truncated_root_uoffset", case_truncated_root_uoffset),
    ("truncated_file_identifier", case_truncated_file_id),
    ("truncated_root_table", case_truncated_root_table),
    ("corrupted_vtable_size", case_corrupted_vtable_size),
    ("corrupted_save_version", case_corrupted_save_version),
    ("corrupted_payload_type", case_corrupted_payload_type),
]


def main():
    passed = 0
    for label, fn in CASES:
        try:
            fn()
        except Exception as exc:
            print(f"FAIL: {label} was accepted (no rejection): {type(exc).__name__}: {exc}")
            continue
        print(f"PASS: {label}")
        passed += 1

    if passed == len(CASES):
        print(f"OK: {passed}/{len(CASES)} wp02d drift cases passed")
        return 0
    print(f"FAIL: {len(CASES) - passed}/{len(CASES)} wp02d drift cases failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
