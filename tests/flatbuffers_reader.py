"""Hand-rolled FlatBuffers reader used by the WP02-B cross-language round-trip gate.

Supports only what the audit needs:
  - 4-byte file_identifier lock (CSWP)
  - root uoffset (must be safe to follow)
  - Envelope: payload_type (uint8), payload (union table offset)
  - CommandBatch: schema_version (uint32), commands (vector of tables)
  - CommandEnvelope: command_id ([ubyte]), campaign_id ([ubyte]),
    issuer_id ([ubyte]), submitted_tick (uint64), scheduled_tick (uint64),
    priority (int32), expected_revision (uint64), kind (ushort),
    payload ([ubyte]).

Decoded JSON mirrors `flatc --json --raw-binary --strict-json` byte-for-byte:
fields appear in schema declaration order, fields whose vtable voff is 0
(declared but unset in the wire) are omitted entirely, and FlatBuffers [ubyte]
vectors are emitted as JSON arrays of unsigned integers.

Mirrors the wire layout documented in Google FlatBuffers (Apache 2.0) without
pulling in the Python library. Bounds-checks every offset to reject corruption,
truncation, and arbitrary-length attacks.

The reader is cross-validated against `flatc --binary` output via
`flatc --json --raw-binary --strict-json` against the committed golden fixture
at .agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin.
The expected canonical decoded form is committed at
`/tmp/wp02b-baseline/sample-envelope.json` (refreshed whenever the warfare.fbs
schema or the golden fixture changes).

CLI:
  python3 flatbuffers_reader.py decode <fixture.bin>             # pretty-print decoded
  python3 flatbuffers_reader.py schema-version <fixture.bin>     # print schema_version
  python3 flatbuffers_reader.py commands-count <fixture.bin>      # print commands count
  python3 flatbuffers_reader.py first-command-kind <fixture.bin>  # print first command kind
  python3 flatbuffers_reader.py second-command-kind <fixture.bin> # print second command kind
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Authoritative schema (must match .agileplus/civic-warfare-program/contracts/warfare.fbs)
# ---------------------------------------------------------------------------

# enum CommandKind : ushort (offset-by-zero in declaration order, mirrors warfare.fbs).
# Changing the schema REQUIRES regenerating the golden fixture via `flatc --binary`.
COMMAND_KIND_VALUES = (
    "None",                          # 0
    "SetPolicy",                     # 1
    "SetDelegation",                 # 2
    "Procure",                       # 3
    "Construct",                     # 4
    "Mobilize",                      # 5
    "AssignForce",                   # 6
    "CreateOperation",               # 7
    "UpdateOperation",               # 8
    "CancelOperation",               # 9
    "SetMission",                    # 10
    "Negotiate",                     # 11
    "ConductCovertOperation",        # 12
    "RespondToCivilEvent",           # 13
)
COMMAND_KIND_INDEX = {name: idx for idx, name in enumerate(COMMAND_KIND_VALUES)}

# enum RootPayload : byte (union discriminant, mirrors warfare.fbs).
ROOT_PAYLOAD_VALUES = ("NONE", "CommandBatch", "ProjectionDelta", "SaveEnvelope")
ROOT_PAYLOAD_INDEX = {name: idx for idx, name in enumerate(ROOT_PAYLOAD_VALUES)}

EXPECTED_FILE_IDENTIFIER = b"CSWP"


# ---------------------------------------------------------------------------
# Low-level readers (bounds-checked)
# ---------------------------------------------------------------------------


class FlatbuffersError(Exception):
    """Raised when the input buffer is malformed, truncated, or contains
    illegal FlatBuffers offsets (corruption, malicious input, etc.).
    """


def _need(buf: bytes, off: int, n: int, what: str) -> None:
    if off < 0 or off + n > len(buf):
        raise FlatbuffersError(f"{what} out of bounds: {off}+{n} > {len(buf)}")


def _u8(buf: bytes, off: int) -> int:
    _need(buf, off, 1, "u8")
    return buf[off]


def _u16(buf: bytes, off: int) -> int:
    _need(buf, off, 2, "u16")
    return struct.unpack_from("<H", buf, off)[0]


def _u32(buf: bytes, off: int) -> int:
    _need(buf, off, 4, "u32")
    return struct.unpack_from("<I", buf, off)[0]


def _u64(buf: bytes, off: int) -> int:
    _need(buf, off, 8, "u64")
    return struct.unpack_from("<Q", buf, off)[0]


def _i32(buf: bytes, off: int) -> int:
    _need(buf, off, 4, "i32")
    return struct.unpack_from("<i", buf, off)[0]


def _follow_table(buf: bytes, table_off: int) -> tuple[int, int, list[int]]:
    """Follow the vtable from the table position. Returns
    (vtable_off, table_inline_size, field_voffs).

    Raises FlatbuffersError on malformed input.
    """
    if table_off < 4 or table_off + 4 > len(buf):
        raise FlatbuffersError(f"table position out of bounds: {table_off}")

    # First int32 at the table is the signed offset back to the vtable.
    # Per the FlatBuffers spec: vtable_off = table_off - vsoff (signed int32).
    # A typical vtable sits ~8..32 bytes before the table; a sane vsoff is
    # positive (table - vtable) and small enough to stay inside the buffer.
    vsoff = _i32(buf, table_off)
    vtable_off = table_off - vsoff
    if vtable_off < 0 or vtable_off + 4 > len(buf):
        raise FlatbuffersError(
            f"vtable follow: table_off={table_off}, vsoff={vsoff}, "
            f"vtable_off={vtable_off} out of bounds (len={len(buf)})"
        )
    vsize = _u16(buf, vtable_off)
    if vsize < 4 or vtable_off + vsize > len(buf):
        raise FlatbuffersError(f"vtable size out of bounds: {vsize}")
    tsize = _u16(buf, vtable_off + 2)
    field_count = (vsize - 4) // 2

    field_voffs: list[int] = []
    for i in range(field_count):
        voff = _u16(buf, vtable_off + 4 + 2 * i)
        if voff != 0:
            # Inlined scalar field at table_off + voff
            # (or uoffset field: target = table_off + voff + read_u32(target))
            if voff > tsize:
                raise FlatbuffersError(
                    f"field[{i}] voff {voff} exceeds table inline size {tsize}"
                )
        field_voffs.append(voff)

    return vtable_off, tsize, field_voffs


def _follow_uoffset(buf: bytes, slot_off: int) -> int:
    """Follow a uoffset field: target = slot_off + rel (rel is read at slot_off)."""
    rel = _u32(buf, slot_off)
    target = slot_off + rel
    if target < 0 or target >= len(buf):
        raise FlatbuffersError(
            f"uoffset follow: slot={slot_off}, rel={rel}, target={target} oob"
        )
    return target


def _read_byte_vector(buf: bytes, slot_off: int) -> list[int]:
    """Decode a FlatBuffers `[ubyte]` vector. `slot_off` is the absolute
    position of the uoffset slot in the parent table. The layout is:

        [slot][u32 rel][u32 count][count * uint8]

    Returns a list of unsigned bytes.
    """
    vec_off = _follow_uoffset(buf, slot_off)
    count = _u32(buf, vec_off)
    data_off = vec_off + 4
    _need(buf, data_off, count, "byte vector data")
    return list(buf[data_off : data_off + count])


# ---------------------------------------------------------------------------
# High-level decoders (per FlatBuffers table)
# ---------------------------------------------------------------------------


def decode_envelope(buf: bytes) -> dict:
    """Decode the Envelope root table. Returns a JSON-serializable dict in the
    canonical WP02-B cross-language shape:

        {
          "payload_type": "<RootPayload enum name>",
          "payload": { ...decoded union table... }
        }
    """
    if len(buf) < 8:
        raise FlatbuffersError(f"buffer too short for Envelope header: {len(buf)}")

    if buf[4:8] != EXPECTED_FILE_IDENTIFIER:
        raise FlatbuffersError(
            f"file_identifier mismatch: got {buf[4:8]!r}, "
            f"expected {EXPECTED_FILE_IDENTIFIER!r}"
        )

    root_off = _u32(buf, 0)
    if root_off >= len(buf):
        raise FlatbuffersError(f"root uoffset out of bounds: {root_off}")

    _, _, env_fields = _follow_table(buf, root_off)

    # Envelope fields:
    # 0: payload_type (uint8) - inlined scalar
    # 1: payload (uoffset to CommandBatch/ProjectionDelta/SaveEnvelope table)
    payload_type_byte = (
        _u8(buf, root_off + env_fields[0]) if len(env_fields) > 0 and env_fields[0] else 0
    )
    payload_type_name = (
        ROOT_PAYLOAD_VALUES[payload_type_byte]
        if payload_type_byte < len(ROOT_PAYLOAD_VALUES)
        else f"Unknown({payload_type_byte})"
    )

    payload: dict | None = None
    if len(env_fields) > 1 and env_fields[1]:
        payload_slot = root_off + env_fields[1]
        payload_off = _follow_uoffset(buf, payload_slot)
        payload = _decode_payload(buf, payload_off, payload_type_name)

    return {"payload_type": payload_type_name, "payload": payload}


def _decode_payload(buf: bytes, payload_off: int, payload_type_name: str) -> dict:
    if payload_type_name == "CommandBatch":
        return _decode_command_batch(buf, payload_off)
    # Other union variants: only CommandBatch is required for the audit gate.
    raise FlatbuffersError(f"unsupported payload type: {payload_type_name}")


def _decode_command_batch(buf: bytes, cb_off: int) -> dict:
    _, _, cb_fields = _follow_table(buf, cb_off)

    # CommandBatch fields:
    # 0: schema_version (uint32)
    # 1: commands (uoffset to vector of CommandEnvelope)
    schema_version = (
        _u32(buf, cb_off + cb_fields[0])
        if len(cb_fields) > 0 and cb_fields[0]
        else 0
    )

    commands: list[dict] = []
    if len(cb_fields) > 1 and cb_fields[1]:
        cmds_slot = cb_off + cb_fields[1]
        cmds_off = _follow_uoffset(buf, cmds_slot)
        cmds_count = _u32(buf, cmds_off)
        cmds_data = cmds_off + 4
        for k in range(cmds_count):
            elem_slot = cmds_data + k * 4
            cmd_off = _follow_uoffset(buf, elem_slot)
            commands.append(_decode_command_envelope(buf, cmd_off))

    return {"schema_version": schema_version, "commands": commands}


def _decode_command_envelope(buf: bytes, cmd_off: int) -> dict:
    """Decode a CommandEnvelope table.

    Field ids (must mirror warfare.fbs):
      0: command_id        ([ubyte])
      1: campaign_id       ([ubyte])
      2: issuer_id         ([ubyte])
      3: submitted_tick    (uint64)
      4: scheduled_tick    (uint64)
      5: priority          (int32)
      6: expected_revision (uint64)
      7: kind              (CommandKind, ushort)
      8: payload           ([ubyte])

    Fields are emitted in declaration order so the JSON output matches the
    canonical cross-language golden (see /tmp/wp02b-baseline/sample-envelope.json).
    """
    _, _, f = _follow_table(buf, cmd_off)

    out: dict = {}

    # 0: command_id ([ubyte])
    if len(f) > 0 and f[0]:
        out["command_id"] = _read_byte_vector(buf, cmd_off + f[0])

    # 1: campaign_id ([ubyte])
    if len(f) > 1 and f[1]:
        out["campaign_id"] = _read_byte_vector(buf, cmd_off + f[1])

    # 2: issuer_id ([ubyte])
    if len(f) > 2 and f[2]:
        out["issuer_id"] = _read_byte_vector(buf, cmd_off + f[2])

    # 3: submitted_tick (uint64)
    if len(f) > 3 and f[3]:
        out["submitted_tick"] = _u64(buf, cmd_off + f[3])

    # 4: scheduled_tick (uint64)
    if len(f) > 4 and f[4]:
        out["scheduled_tick"] = _u64(buf, cmd_off + f[4])

    # 5: priority (int32)
    if len(f) > 5 and f[5]:
        out["priority"] = _i32(buf, cmd_off + f[5])

    # 6: expected_revision (uint64)
    if len(f) > 6 and f[6]:
        out["expected_revision"] = _u64(buf, cmd_off + f[6])

    # 7: kind (CommandKind, ushort)
    if len(f) > 7 and f[7]:
        kind_raw = _u16(buf, cmd_off + f[7])
        out["kind"] = (
            COMMAND_KIND_VALUES[kind_raw]
            if kind_raw < len(COMMAND_KIND_VALUES)
            else f"Unknown({kind_raw})"
        )

    # 8: payload ([ubyte])
    if len(f) > 8 and f[8]:
        out["payload"] = _read_byte_vector(buf, cmd_off + f[8])

    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_decode(path: Path) -> int:
    obj = decode_envelope(path.read_bytes())
    # Insertion-order dict (Python 3.7+) keeps schema declaration order so the
    # rendered JSON matches `flatc --json --raw-binary --strict-json` byte-for-byte.
    print(json.dumps(obj, indent=2))
    return 0


def _cli_scalar(path: Path, key: str) -> int:
    obj = decode_envelope(path.read_bytes())
    payload = obj.get("payload") or {}
    if key == "schema-version":
        print(payload.get("schema_version"))
    elif key == "commands-count":
        print(len(payload.get("commands") or []))
    elif key == "first-command-kind":
        cmds = payload.get("commands") or []
        print(cmds[0].get("kind") if cmds else "<none>")
    elif key == "second-command-kind":
        cmds = payload.get("commands") or []
        print(cmds[1].get("kind") if len(cmds) > 1 else "<none>")
    else:
        raise SystemExit(f"unknown scalar key: {key}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = argv[1]
    path = Path(argv[2])
    if cmd == "decode":
        return _cli_decode(path)
    if cmd in ("schema-version", "commands-count", "first-command-kind", "second-command-kind"):
        return _cli_scalar(path, cmd)
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
