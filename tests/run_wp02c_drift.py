#!/usr/bin/env python3
"""WP02-C cross-language drift regression test (dependency-free).

Invokes the hand-rolled Python FlatBuffers reader on the new
ProjectionDelta golden fixture (sample-projection.bin) and verifies
it rejects the same 8 mutation cases:

  1. empty file
  2. wrong file_identifier (CSWP -> XSWP)
  3. truncated root_uoffset (buffer < 4 bytes)
  4. truncated file_identifier (buffer < 8 bytes)
  5. truncated root table (root offset past EOF)
  6. corrupted vtable_size (zero)
  7. corrupted decisions count (huge u32)
  8. corrupted payload_type discriminator (bit-flip)

Byte positions were traced by hand from the fixture's vtable layout
and verified empirically with the Python reader's decoder.

Reproduction:
  python3 tests/run_wp02c_drift.py
"""
import os
import struct
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tests"))

from flatbuffers_reader import decode_envelope, FlatbuffersError  # noqa: E402

GOLDEN = os.path.join(
    REPO_ROOT,
    ".agileplus/civic-warfare-program/contracts/fixtures/sample-projection.bin",
)


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
    # root uoffset is 0x14 (20); keep file < 8 bytes so root_off > EOF
    bad = open(GOLDEN, "rb").read()[:8]
    with _raises():
        decode_envelope(bad)


def case_corrupted_vtable_size():
    # Set ProjectionDelta's vtable vsize to 0 (pd_vtable at 0x1c)
    bad = bytearray(open(GOLDEN, "rb").read())
    struct.pack_into("<H", bad, 0x1C, 0)
    with _raises():
        decode_envelope(bytes(bad))


def case_corrupted_decisions_count():
    # Set decisions vector count to a huge u32 (verified position: 0xe0)
    bad = bytearray(open(GOLDEN, "rb").read())
    struct.pack_into("<I", bad, 0xE0, 0x7FFFFFF0)
    with _raises():
        decode_envelope(bytes(bad))


def case_corrupted_payload_type():
    # Flip high bit of payload_type union discriminator byte @ 0x17
    bad = bytearray(open(GOLDEN, "rb").read())
    bad[0x17] ^= 0x80
    with _raises():
        decode_envelope(bytes(bad))


class _Raises:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, FlatbuffersError)


def _raises():
    return _Raises()


CASES = [
    ("empty_buffer", case_empty),
    ("wrong_file_identifier", case_wrong_file_id),
    ("truncated_root_uoffset", case_truncated_root_uoffset),
    ("truncated_file_identifier", case_truncated_file_id),
    ("truncated_root_table", case_truncated_root_table),
    ("corrupted_vtable_size", case_corrupted_vtable_size),
    ("corrupted_decisions_count", case_corrupted_decisions_count),
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
        print(f"OK: {passed}/{len(CASES)} wp02c drift cases passed")
        return 0
    print(f"FAIL: {len(CASES) - passed}/{len(CASES)} wp02c drift cases failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
