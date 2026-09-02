#!/usr/bin/env python3
"""
Hand-rolled Python FlatBuffers reader for the warfare program wire contracts.

Cross-validated against `flatc --json --raw-binary --strict-json` of the
golden fixtures committed in
`.agileplus/civic-warfare-program/contracts/fixtures/`.

Supports:
  - Envelope (root) with RootPayload union
    - CommandBatch  (schema_version + commands vector of CommandEnvelope)
    - ProjectionDelta (campaign_id..explanations + decisions/outcomes tables)
    - SaveEnvelope  (abi_version, save_version, tick, revision, ...)

The reader only depends on the Python stdlib (struct, sys, json, os, hashlib).
"""

import json
import os
import struct
import sys


# Schema enum tables (mirror of warfare.fbs)
COMMAND_KIND = [
    "None",
    "SetPolicy",
    "SetDelegation",
    "Procure",
    "Construct",
    "Mobilize",
    "AssignForce",
    "CreateOperation",
    "UpdateOperation",
    "CancelOperation",
    "SetMission",
    "Negotiate",
    "ConductCovertOperation",
    "RespondToCivilEvent",
]

DECISION_CODE = [
    "Accepted",
    "Duplicate",
    "RevisionConflict",
    "Unauthorized",
    "InvalidConfiguration",
    "MissingPrerequisite",
    "InsufficientResources",
    "InvalidTarget",
    "Expired",
    "RejectedByPolicy",
]

ROOT_PAYLOAD_KIND = {
    0: "NONE",
    1: "CommandBatch",
    2: "ProjectionDelta",
    3: "SaveEnvelope",
}


class FlatbuffersError(Exception):
    """Raised on any wire-format violation (truncation, corruption, etc.)."""


# ---------- low-level readers ----------


def _u8(buf, off):
    if off < 0 or off + 1 > len(buf):
        raise FlatbuffersError(f"u8 out of range at {off}")
    return buf[off]


def _i8(buf, off):
    v = _u8(buf, off)
    return v - 256 if v >= 128 else v


def _u16(buf, off):
    if off < 0 or off + 2 > len(buf):
        raise FlatbuffersError(f"u16 out of range at {off}")
    return struct.unpack_from("<H", buf, off)[0]


def _i16(buf, off):
    if off < 0 or off + 2 > len(buf):
        raise FlatbuffersError(f"i16 out of range at {off}")
    return struct.unpack_from("<h", buf, off)[0]


def _u32(buf, off):
    if off < 0 or off + 4 > len(buf):
        raise FlatbuffersError(f"u32 out of range at {off}")
    return struct.unpack_from("<I", buf, off)[0]


def _u64(buf, off):
    if off < 0 or off + 8 > len(buf):
        raise FlatbuffersError(f"u64 out of range at {off}")
    return struct.unpack_from("<Q", buf, off)[0]


def _soff(buf, off):
    """Signed soffset (int32). The first int32 at a table is the vtable soffset."""
    if off < 0 or off + 4 > len(buf):
        raise FlatbuffersError(f"soff out of range at {off}")
    return struct.unpack_from("<i", buf, off)[0]


# ---------- vtable / table / vector helpers ----------


def _read_vtable(buf, table_off):
    """Return (vtable_off, vtable_size, table_size, fields_list)."""
    soff = _soff(buf, table_off)
    # vtable position = table_off - soff (per spec, soff points back)
    vtable_off = table_off - soff
    if vtable_off < 0 or vtable_off + 4 > len(buf):
        raise FlatbuffersError(f"vtable underflow at table_off={table_off}, soff={soff}")
    vsize = _u16(buf, vtable_off)
    tsize = _u16(buf, vtable_off + 2)
    fields = []
    for i in range((vsize - 4) // 2):
        if vtable_off + 4 + 2 * i + 2 > len(buf):
            raise FlatbuffersError(f"vtable field[{i}] out of range")
        fields.append(_u16(buf, vtable_off + 4 + 2 * i))
    return vtable_off, vsize, tsize, fields


def _read_uoffset(buf, slot):
    """Read a uoffset32 at `slot`; return absolute target position."""
    rel = _u32(buf, slot)
    return slot + rel


def _read_vector_count(buf, vec_data):
    return _u32(buf, vec_data)


def _read_vector_bytes(buf, vec_data):
    count = _u32(buf, vec_data)
    start = vec_data + 4
    if start + count > len(buf):
        raise FlatbuffersError(f"byte vector count {count} past EOF at {vec_data}")
    return list(buf[start : start + count])


def _read_vector_uoffsets(buf, vec_data):
    """Vector of uoffsets (offsets to tables). Returns absolute target positions."""
    count = _u32(buf, vec_data)
    start = vec_data + 4
    targets = []
    for i in range(count):
        slot = start + 4 * i
        if slot + 4 > len(buf):
            raise FlatbuffersError(f"uoffset vector slot {slot} past EOF")
        targets.append(slot + _u32(buf, slot))
    return targets


def _read_vector_strings(buf, vec_data):
    """Vector of strings (uoffset to byte vector of utf-8 bytes)."""
    count = _u32(buf, vec_data)
    start = vec_data + 4
    out = []
    for i in range(count):
        slot = start + 4 * i
        rel = _u32(buf, slot)
        target = slot + rel
        out.append(_read_string_at(buf, target))
    return out


def _read_string_at(buf, str_off):
    """Read a FlatBuffers string at the given offset."""
    length = _u32(buf, str_off)
    start = str_off + 4
    if start + length > len(buf):
        raise FlatbuffersError(f"string length {length} past EOF at {str_off}")
    return buf[start : start + length].decode("utf-8", errors="replace")


def _read_table_byte_vec_field(buf, table_off, fields, idx):
    """Return the byte vector at field idx, or [] if not set."""
    if idx >= len(fields) or fields[idx] == 0:
        return []
    slot = table_off + fields[idx]
    target = _read_uoffset(buf, slot)
    return _read_vector_bytes(buf, target)


def _read_table_u32_field(buf, table_off, fields, idx):
    if idx >= len(fields) or fields[idx] == 0:
        return 0
    return _u32(buf, table_off + fields[idx])


def _read_table_u64_field(buf, table_off, fields, idx):
    if idx >= len(fields) or fields[idx] == 0:
        return 0
    return _u64(buf, table_off + fields[idx])


def _read_table_u16_field(buf, table_off, fields, idx):
    if idx >= len(fields) or fields[idx] == 0:
        return 0
    return _u16(buf, table_off + fields[idx])


def _read_table_i32_field(buf, table_off, fields, idx):
    if idx >= len(fields) or fields[idx] == 0:
        return 0
    raw = _u32(buf, table_off + fields[idx])
    return raw - 0x1_0000_0000 if raw >= 0x8000_0000 else raw


def _read_table_string_field(buf, table_off, fields, idx):
    if idx >= len(fields) or fields[idx] == 0:
        return ""
    slot = table_off + fields[idx]
    target = _read_uoffset(buf, slot)
    return _read_string_at(buf, target)


def _read_table_uoffset_field_target(buf, table_off, fields, idx):
    """Return the absolute target of a uoffset field, or None if not set."""
    if idx >= len(fields) or fields[idx] == 0:
        return None
    slot = table_off + fields[idx]
    return _read_uoffset(buf, slot)


# ---------- per-table decoders ----------


def _decode_command_envelope(buf, cmd_off):
    """Decode CommandEnvelope at cmd_off; return dict."""
    _, _, _, fields = _read_vtable(buf, cmd_off)
    command_id = _read_table_byte_vec_field(buf, cmd_off, fields, 0)
    campaign_id = _read_table_byte_vec_field(buf, cmd_off, fields, 1)
    issuer_id = _read_table_byte_vec_field(buf, cmd_off, fields, 2)
    submitted_tick = _read_table_u64_field(buf, cmd_off, fields, 3)
    scheduled_tick = _read_table_u64_field(buf, cmd_off, fields, 4)
    priority = _read_table_i32_field(buf, cmd_off, fields, 5)
    expected_revision = _read_table_u64_field(buf, cmd_off, fields, 6)
    kind_idx = _read_table_u16_field(buf, cmd_off, fields, 7)
    kind_name = COMMAND_KIND[kind_idx] if kind_idx < len(COMMAND_KIND) else f"Unknown({kind_idx})"
    payload = _read_table_byte_vec_field(buf, cmd_off, fields, 8)
    return {
        "command_id": command_id,
        "campaign_id": campaign_id,
        "issuer_id": issuer_id,
        "submitted_tick": submitted_tick,
        "scheduled_tick": scheduled_tick,
        "priority": priority,
        "expected_revision": expected_revision,
        "kind": kind_name,
        "payload": payload,
    }


def _decode_command_batch(buf, cb_off):
    """Decode CommandBatch at cb_off; return dict."""
    _, _, _, fields = _read_vtable(buf, cb_off)
    schema_version = _read_table_u32_field(buf, cb_off, fields, 0)
    commands = []
    cmds_vec_target = _read_table_uoffset_field_target(buf, cb_off, fields, 1)
    if cmds_vec_target is not None:
        cmd_offsets = _read_vector_uoffsets(buf, cmds_vec_target)
        for cmd_off in cmd_offsets:
            commands.append(_decode_command_envelope(buf, cmd_off))
    return {"schema_version": schema_version, "commands": commands}


def _decode_command_decision(buf, cd_off):
    _, _, _, fields = _read_vtable(buf, cd_off)
    command_id = _read_table_byte_vec_field(buf, cd_off, fields, 0)
    code_idx = _read_table_u16_field(buf, cd_off, fields, 1)
    code_name = (
        DECISION_CODE[code_idx] if code_idx < len(DECISION_CODE) else f"Unknown({code_idx})"
    )
    reason_key = _read_table_string_field(buf, cd_off, fields, 2)
    validated_revision = _read_table_u64_field(buf, cd_off, fields, 3)
    details = _read_table_byte_vec_field(buf, cd_off, fields, 4)
    return {
        "command_id": command_id,
        "code": code_name,
        "reason_key": reason_key,
        "validated_revision": validated_revision,
        "details": details,
    }


def _decode_outcome_envelope(buf, oe_off):
    _, _, _, fields = _read_vtable(buf, oe_off)
    command_id = _read_table_byte_vec_field(buf, oe_off, fields, 0)
    tick = _read_table_u64_field(buf, oe_off, fields, 1)
    sequence = _read_table_u64_field(buf, oe_off, fields, 2)
    context = _read_table_u16_field(buf, oe_off, fields, 3)
    kind = _read_table_u16_field(buf, oe_off, fields, 4)
    payload = _read_table_byte_vec_field(buf, oe_off, fields, 5)
    return {
        "command_id": command_id,
        "tick": tick,
        "sequence": sequence,
        "context": context,
        "kind": kind,
        "payload": payload,
    }


def _decode_projection_delta(buf, pd_off):
    _, _, _, fields = _read_vtable(buf, pd_off)
    campaign_id = _read_table_byte_vec_field(buf, pd_off, fields, 0)
    observer_id = _read_table_byte_vec_field(buf, pd_off, fields, 1)
    base_revision = _read_table_u64_field(buf, pd_off, fields, 2)
    new_revision = _read_table_u64_field(buf, pd_off, fields, 3)
    tick = _read_table_u64_field(buf, pd_off, fields, 4)
    state_hash = _read_table_byte_vec_field(buf, pd_off, fields, 5)

    decisions = []
    dec_vec = _read_table_uoffset_field_target(buf, pd_off, fields, 6)
    if dec_vec is not None:
        for cd_off in _read_vector_uoffsets(buf, dec_vec):
            decisions.append(_decode_command_decision(buf, cd_off))

    outcomes = []
    out_vec = _read_table_uoffset_field_target(buf, pd_off, fields, 7)
    if out_vec is not None:
        for oe_off in _read_vector_uoffsets(buf, out_vec):
            outcomes.append(_decode_outcome_envelope(buf, oe_off))

    views = _read_table_byte_vec_field(buf, pd_off, fields, 8)
    removals = _read_table_byte_vec_field(buf, pd_off, fields, 9)
    alerts = _read_table_byte_vec_field(buf, pd_off, fields, 10)
    explanations = _read_table_byte_vec_field(buf, pd_off, fields, 11)

    return {
        "campaign_id": campaign_id,
        "observer_id": observer_id,
        "base_revision": base_revision,
        "new_revision": new_revision,
        "tick": tick,
        "state_hash": state_hash,
        "decisions": decisions,
        "outcomes": outcomes,
        "views": views,
        "removals": removals,
        "alerts": alerts,
        "explanations": explanations,
    }


def _decode_save_envelope(buf, se_off):
    _, _, _, fields = _read_vtable(buf, se_off)
    abi_version = _read_table_u32_field(buf, se_off, fields, 0)
    schema_version = _read_table_u32_field(buf, se_off, fields, 1)
    save_version = _read_table_u32_field(buf, se_off, fields, 2)
    rng_version = _read_table_u32_field(buf, se_off, fields, 3)
    campaign_id = _read_table_byte_vec_field(buf, se_off, fields, 4)
    rules_manifest_hash = _read_table_byte_vec_field(buf, se_off, fields, 5)
    tick = _read_table_u64_field(buf, se_off, fields, 6)
    revision = _read_table_u64_field(buf, se_off, fields, 7)
    return {
        "abi_version": abi_version,
        "schema_version": schema_version,
        "save_version": save_version,
        "rng_version": rng_version,
        "campaign_id": campaign_id,
        "rules_manifest_hash": rules_manifest_hash,
        "tick": tick,
        "revision": revision,
    }


# ---------- envelope (root) ----------


def decode_envelope(buf):
    """Decode the root Envelope; return dict {payload_type, payload}."""
    if not isinstance(buf, (bytes, bytearray, memoryview)):
        raise TypeError("buf must be bytes-like")
    if len(buf) < 8:
        raise FlatbuffersError(f"buffer too small ({len(buf)} bytes); need >= 8")
    if buf[4:8] != b"CSWP":
        raise FlatbuffersError(
            f"file_identifier mismatch: got {buf[4:8]!r}, expected b'CSWP'"
        )
    root_off = _u32(buf, 0)
    if root_off >= len(buf):
        raise FlatbuffersError(f"root_off {root_off} >= len {len(buf)}")
    _, _, _, fields = _read_vtable(buf, root_off)
    # Field 0: payload_type (inline uint8 at root_off + voff)
    if len(fields) < 1 or fields[0] == 0:
        raise FlatbuffersError("payload_type field not set")
    type_byte = _u8(buf, root_off + fields[0])
    # Field 1: payload (uoffset slot)
    if len(fields) < 2 or fields[1] == 0:
        raise FlatbuffersError("payload uoffset field not set")
    payload_slot = root_off + fields[1]
    payload_target = _read_uoffset(buf, payload_slot)

    payload_type = ROOT_PAYLOAD_KIND.get(type_byte, f"Unknown({type_byte})")
    if payload_type == "CommandBatch":
        payload = _decode_command_batch(buf, payload_target)
    elif payload_type == "ProjectionDelta":
        payload = _decode_projection_delta(buf, payload_target)
    elif payload_type == "SaveEnvelope":
        payload = _decode_save_envelope(buf, payload_target)
    else:
        raise FlatbuffersError(f"unsupported payload_type: {payload_type}")
    return {"payload_type": payload_type, "payload": payload}


# ---------- CLI ----------


def main(argv):
    if len(argv) < 3 or argv[1] != "decode":
        print("usage: flatbuffers_reader.py decode <fixture.bin>", file=sys.stderr)
        return 2
    path = argv[2]
    with open(path, "rb") as f:
        buf = f.read()
    out = decode_envelope(buf)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
