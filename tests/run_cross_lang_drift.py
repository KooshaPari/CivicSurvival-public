#!/usr/bin/env python3
"""WP02-B cross-language drift runner — dependency-free twin of
tests/test_cross_lang_drift.py for use in CI runners that don't have
pytest installed (e.g., the public-audit GitHub workflow).

Mirrors the 9 mutation cases from the pytest version; passes if and
only if every expected rejection fires on the Python reader.

Exit codes:
  0 — all 9 cases behaved as expected (8 rejections + 1 positive)
  1 — at least one case failed (read pass; means a bug in the reader)

Stdout (one line per case):
  PASS: <name>
  FAIL: <name> -- <error>
"""
from __future__ import annotations

import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from flatbuffers_reader import FlatbuffersError, decode_envelope  # noqa: E402

GOLDEN = os.path.join(
    ROOT,
    ".agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin",
)


def _read() -> bytes:
    with open(GOLDEN, "rb") as f:
        return f.read()


def _find_uint16(buf: bytes, target: int) -> int:
    for i in range(8, len(buf) - 2):
        if int.from_bytes(buf[i : i + 2], "little") == target:
            return i
    raise AssertionError(f"uint16={target} not found in fixture")


def _find_vector_count(buf: bytes) -> int:
    for i in range(8, len(buf) - 8):
        if int.from_bytes(buf[i : i + 4], "little") == 2:
            uoff1 = int.from_bytes(buf[i + 4 : i + 8], "little")
            if 0 < uoff1 < 256:
                return i
    raise AssertionError("vector count=2 not found in fixture")


def _expect_reject(name: str, mutate):
    try:
        mutate()
    except FlatbuffersError:
        print(f"PASS: {name}")
        return True
    except Exception as ex:  # noqa: BLE001
        print(f"FAIL: {name} -- raised {type(ex).__name__}: {ex} (expected FlatbuffersError)")
        return False
    print(f"FAIL: {name} -- no exception raised (expected FlatbuffersError)")
    return False


def _expect_pass(name: str, mutate):
    try:
        mutate()
    except Exception as ex:  # noqa: BLE001
        print(f"FAIL: {name} -- raised {type(ex).__name__}: {ex} (expected success)")
        return False
    print(f"PASS: {name}")
    return True


CASES = [
    (
        "test_rejects_empty_buffer",
        lambda: _expect_reject(
            "test_rejects_empty_buffer",
            lambda: decode_envelope(b""),
        ),
    ),
    (
        "test_rejects_wrong_file_identifier",
        lambda: _expect_reject(
            "test_rejects_wrong_file_identifier",
            lambda: _mutate_file_identifier(),
        ),
    ),
    (
        "test_rejects_truncated_root_uoffset",
        lambda: _expect_reject(
            "test_rejects_truncated_root_uoffset",
            lambda: decode_envelope(_read()[:3]),
        ),
    ),
    (
        "test_rejects_truncated_file_identifier",
        lambda: _expect_reject(
            "test_rejects_truncated_file_identifier",
            lambda: decode_envelope(_read()[:7]),
        ),
    ),
    (
        "test_rejects_truncated_root_table",
        lambda: _expect_reject(
            "test_rejects_truncated_root_table",
            lambda: _mutate_root_past_eof(),
        ),
    ),
    (
        "test_rejects_corrupted_vector_count",
        lambda: _expect_reject(
            "test_rejects_corrupted_vector_count",
            lambda: _mutate_vector_count(),
        ),
    ),
    (
        "test_rejects_corrupted_schema_version",
        lambda: _expect_reject(
            "test_rejects_corrupted_schema_version",
            lambda: _mutate_schema_version(),
        ),
    ),
    (
        "test_rejects_corrupted_file_identifier_bit_flip",
        lambda: _expect_reject(
            "test_rejects_corrupted_file_identifier_bit_flip",
            lambda: _mutate_file_identifier_bit_flip(),
        ),
    ),
    (
        "test_canonical_fixture_decodes",
        lambda: _expect_pass(
            "test_canonical_fixture_decodes",
            lambda: _assert_canonical_decodes(),
        ),
    ),
]


def _mutate_file_identifier():
    buf = bytearray(_read())
    buf[4] = ord("C")
    buf[5] = ord("S")
    buf[6] = ord("C")  # was 'W'
    buf[7] = ord("P")
    decode_envelope(bytes(buf))


def _mutate_root_past_eof():
    buf = bytearray(_read())
    struct.pack_into("<I", buf, 0, len(buf) + 32)
    decode_envelope(bytes(buf))


def _mutate_vector_count():
    buf = bytearray(_read())
    pos = _find_vector_count(buf)
    struct.pack_into("<I", buf, pos, 0x7FFFFFFF)
    decode_envelope(bytes(buf))


def _mutate_schema_version():
    buf = bytearray(_read())
    pos = _find_uint16(buf, 7)
    struct.pack_into("<H", buf, pos, 0xFFFF)
    decode_envelope(bytes(buf))


def _mutate_file_identifier_bit_flip():
    buf = bytearray(_read())
    buf[5] ^= 0x01  # 'S' (0x53) -> 'T' (0x52)
    decode_envelope(bytes(buf))


def _assert_canonical_decodes():
    out = decode_envelope(_read())
    payload = out["payload"]
    assert out["payload_type"] == "CommandBatch", (
        f"unexpected payload_type: {out['payload_type']!r}"
    )
    assert payload["schema_version"] == 7, (
        f"unexpected schema_version: {payload['schema_version']!r}"
    )
    assert len(payload["commands"]) == 2, (
        f"unexpected command count: {len(payload['commands'])!r}"
    )
    assert [c["kind"] for c in payload["commands"]] == ["SetMission", "Negotiate"], (
        f"unexpected kinds: {[c['kind'] for c in payload['commands']]!r}"
    )


def main() -> int:
    failures = 0
    for _name, fn in CASES:
        try:
            ok = fn()
        except AssertionError as ex:
            print(f"FAIL: {_name} -- assertion: {ex}")
            ok = False
        except Exception as ex:  # noqa: BLE001
            print(f"FAIL: {_name} -- {type(ex).__name__}: {ex}")
            ok = False
        if not ok:
            failures += 1
    if failures:
        print(f"FAILED {failures}/{len(CASES)} cross-lang drift cases", file=sys.stderr)
        return 1
    print(f"OK: {len(CASES)}/{len(CASES)} cross-lang drift cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
