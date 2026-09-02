#!/usr/bin/env python3
"""WP02-B cross-language drift test — proves the Python FlatBuffers reader rejects
corrupt, truncated, and mutated versions of the golden fixture.

These mutation cases are the same shape as the C# drift test in
tests/public-audit/test_flatbuffers_roundtrip_drift.sh: any failure of one
language to reject a mutation that flatc rejects means the readers are not
actually equivalent to the canonical FlatBuffers wire format.
"""

import json
import os
import struct
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from flatbuffers_reader import FlatbuffersError, decode_envelope


GOLDEN_PATH = ".agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin"


def _read_golden_bytes() -> bytes:
    with open(GOLDEN_PATH, "rb") as f:
        return f.read()


def _find_schema_version_offset(buf: bytes) -> int:
    """Locate the schema_version=7 inline uint16 by scanning the inlined scalars."""
    for i in range(8, len(buf) - 2):
        if int.from_bytes(buf[i : i + 2], "little") == 7:
            return i
    raise AssertionError("schema_version=7 not found in fixture")


def _find_vector_count_offset(buf: bytes) -> int:
    """Locate the commands vector count=2 by finding u32=2 followed by a valid uoffset."""
    for i in range(8, len(buf) - 8):
        if int.from_bytes(buf[i : i + 4], "little") == 2:
            uoff1 = int.from_bytes(buf[i + 4 : i + 8], "little")
            if 0 < uoff1 < 256:
                return i
    raise AssertionError("vector count=2 not found in fixture")


def _decoded_canonical_payload(buf: bytes) -> dict:
    """Decode the canonical fixture; assumes the file decodes cleanly."""
    out = decode_envelope(buf)
    assert out["payload_type"] == "CommandBatch", (
        f"unexpected payload_type: {out['payload_type']!r}"
    )
    return out["payload"]


# --- 8 mutation cases -------------------------------------------------------


def test_rejects_empty_buffer():
    with pytest.raises(FlatbuffersError):
        decode_envelope(b"")


def test_rejects_wrong_file_identifier():
    buf = bytearray(_read_golden_bytes())
    # bytes 4..8 are the file_identifier 'CSWP'
    buf[4] = ord("C")
    buf[5] = ord("S")
    buf[6] = ord("C")  # was 'W'
    buf[7] = ord("P")
    with pytest.raises(FlatbuffersError):
        decode_envelope(bytes(buf))


def test_rejects_truncated_root_uoffset():
    buf = _read_golden_bytes()
    # < 4 bytes → no root uoffset
    with pytest.raises(FlatbuffersError):
        decode_envelope(buf[:3])


def test_rejects_truncated_file_identifier():
    buf = _read_golden_bytes()
    # 4..7 bytes → no file_identifier
    with pytest.raises(FlatbuffersError):
        decode_envelope(buf[:7])


def test_rejects_truncated_root_table():
    buf = _read_golden_bytes()
    # Root uoffset points past EOF
    data = bytearray(buf)
    struct.pack_into("<I", data, 0, len(buf) + 32)
    with pytest.raises(FlatbuffersError):
        decode_envelope(bytes(data))


def test_rejects_corrupted_vector_count():
    buf = bytearray(_read_golden_bytes())
    pos = _find_vector_count_offset(buf)
    struct.pack_into("<I", buf, pos, 0x7FFFFFFF)  # 2 billion commands
    with pytest.raises(FlatbuffersError):
        decode_envelope(bytes(buf))


def test_rejects_corrupted_schema_version():
    buf = bytearray(_read_golden_bytes())
    pos = _find_schema_version_offset(buf)
    # Flip the high bit — schema_version 7 becomes a huge value
    struct.pack_into("<H", buf, pos, 0xFFFF)
    with pytest.raises(FlatbuffersError):
        decode_envelope(bytes(buf))


def test_rejects_corrupted_file_identifier_bit_flip():
    buf = bytearray(_read_golden_bytes())
    # Single bit-flip on a file_identifier byte (still 4 ASCII letters)
    buf[5] ^= 0x01  # 'S' (0x53) → 'T' (0x52)
    with pytest.raises(FlatbuffersError):
        decode_envelope(bytes(buf))


# --- 1 positive round-trip case (must succeed) -------------------------------


def test_canonical_fixture_decodes():
    """Sanity: the Python reader can decode the golden fixture exactly."""
    out = _decoded_canonical_payload(_read_golden_bytes())
    assert out["schema_version"] == 7
    assert len(out["commands"]) == 2
    assert [c["kind"] for c in out["commands"]] == ["SetMission", "Negotiate"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))