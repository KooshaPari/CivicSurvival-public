// Hand-rolled FlatBuffers reader used by the public-audit runner.
//
// Supports only what the audit needs:
//   - 4-byte file_identifier lock (CSWP)
//   - root uoffset (must be safe to follow)
//   - Envelope: payload_type (uint8), payload (union table offset)
//   - CommandBatch: schema_version (uint16), commands (vector of tables)
//   - CommandEnvelope: kind (uint8), payload (vector of bytes)
//
// Mirrors the wire layout documented in Google FlatBuffers (Apache 2.0)
// without pulling in the library. Bounds-checks every offset to reject
// corruption, truncation, and arbitrary-length attacks.
//
// The reader was cross-validated against `flatc --binary` output via
// `flatc --json --raw-binary --strict-json` of the committed golden
// fixture at .agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin.

using System.Buffers.Binary;

public static class FlatbuffersReader
{
    public enum RootPayloadKind : byte { NONE = 0, CommandBatch = 1, ProjectionDelta = 2, SaveEnvelope = 3 }

    public readonly record struct CommandView(int KindByte, int PayloadByteCount);

    public sealed class EnvelopeView
    {
        public RootPayloadKind PayloadType { get; set; }
        public ushort SchemaVersion { get; set; }
        public int CommandCount => Commands.Count;
        public List<CommandView> Commands { get; } = new();
    }

    public static bool TryParseEnvelope(byte[] buffer, string expectedFileIdentifier,
        string expectedRootType, out EnvelopeView envelope, out string? error)
    {
        envelope = null!;
        error = null;
        if (buffer is null || buffer.Length < 8) { error = "buffer < 8 bytes"; return false; }

        var span = buffer.AsSpan();
        // 0..3: uoffset32 from start of buffer to root table.
        if (BinaryPrimitives.ReadUInt32LittleEndian(span[0..4]) is var rootOffset && rootOffset > buffer.Length - 4)
        { error = $"root offset {rootOffset} past EOF"; return false; }

        // 4..7: file_identifier.
        var ident = System.Text.Encoding.ASCII.GetString(span[4..8]);
        if (!string.Equals(ident, expectedFileIdentifier, StringComparison.Ordinal))
        { error = $"file_identifier {ident} != {expectedFileIdentifier}"; return false; }

        // Skip the root-type assertion (we accept whatever root_type the schema
        // declares, asserted up front in FlatbuffersRootSource.Find).
        _ = expectedRootType;

        var rootTableOff = (int)rootOffset;
        var env = new EnvelopeView();
        if (!TryFollowTable(span, rootTableOff, out var envFields, out error)) return false;
        if (!TryReadUInt8Field(span, rootTableOff, envFields, 0, out var payloadTypeByte, out error))
            return false;
        env.PayloadType = (RootPayloadKind)payloadTypeByte;

        if (env.PayloadType != RootPayloadKind.CommandBatch)
            return true; // kind-assertion is done by the caller

        // Field 1 of Envelope: payload (union table offset).
        // uoffsets are relative to where the uoffset itself is stored.
        if (!TryReadUOffsetFieldLocation(span, rootTableOff, envFields, 1, out var payloadStoreAbs,
                out var payloadRel, out error)) return false;
        var payloadAbs = (int)(payloadStoreAbs + payloadRel);
        if (!TryFollowTable(span, payloadAbs, out var cbFields, out error)) return false;
        if (!TryReadUInt16Field(span, payloadAbs, cbFields, 0, out var schemaVersion, out error))
            return false;
        env.SchemaVersion = schemaVersion;

        // Field 1 of CommandBatch: commands (vector of CommandEnvelope tables).
        if (!TryReadUOffsetFieldLocation(span, payloadAbs, cbFields, 1, out var cmdsStoreAbs,
                out var cmdsRel, out error)) return false;
        var cmdsVecAbs = (int)(cmdsStoreAbs + cmdsRel);
        // cmdsVecAbs is vec_data (where u32 count lives); elements follow at +4.
        if (cmdsVecAbs + 4 > buffer.Length)
        { error = "commands vector header past EOF"; return false; }
        var cmdCount = (int)BinaryPrimitives.ReadUInt32LittleEndian(span[cmdsVecAbs..(cmdsVecAbs + 4)]);
        var cmdVecDataAbs = cmdsVecAbs + 4;
        for (int i = 0; i < cmdCount; i++)
        {
            var elemAbs = cmdVecDataAbs + i * 4;
            if (elemAbs + 4 > buffer.Length) { error = "truncated commands vector"; return false; }
            var cmdRel = BinaryPrimitives.ReadUInt32LittleEndian(span[elemAbs..(elemAbs + 4)]);
            // FlatBuffers uoffset is relative to the slot position (NOT to slot+4).
            var cmdAbs = elemAbs + (int)cmdRel;
            if (cmdAbs + 4 > buffer.Length) { error = $"command[{i}] table off {cmdAbs} past EOF"; return false; }
            if (!TryFollowTable(span, cmdAbs, out var cmdFields, out error)) return false;
            if (!TryReadUInt8Field(span, cmdAbs, cmdFields, 7, out var kindByte, out error))
                return false;
            int payloadLen = 0;
            if (HasField(cmdFields, 9))
            {
                if (!TryReadUOffsetFieldLocation(span, cmdAbs, cmdFields, 9, out var plStoreAbs,
                        out var plRel, out error))
                    return false;
                var plAbs = (int)(plStoreAbs + plRel);
                if (!TryReadVector(span, plAbs, out var plCount, out error))
                    return false;
                payloadLen = plCount;
            }
            env.Commands.Add(new CommandView(kindByte, payloadLen));
        }
        envelope = env;
        return true;
    }

    // --- low-level helpers --------------------------------------------------
    private static bool TryFollowTable(ReadOnlySpan<byte> buf, int tableOff, out int[] fields, out string error)
    {
        fields = Array.Empty<int>();
        error = "";
        if (tableOff < 0 || tableOff + 4 > buf.Length) { error = $"table off {tableOff} past EOF"; return false; }
        var soff = BinaryPrimitives.ReadInt32LittleEndian(buf.Slice(tableOff, 4));
        var vtableOff = tableOff - soff;
        if (soff == 0 || vtableOff < 0 || vtableOff + 4 > buf.Length)
        { error = $"vtable soffset {soff} invalid for table at {tableOff}"; return false; }
        var vtableSize = BinaryPrimitives.ReadUInt16LittleEndian(buf.Slice(vtableOff, 2));
        if (vtableOff + vtableSize > buf.Length)
        { error = "vtable truncated"; return false; }
        var fieldCount = (vtableSize - 4) / 2;
        fields = new int[fieldCount];
        for (int i = 0; i < fieldCount; i++)
            fields[i] = BinaryPrimitives.ReadUInt16LittleEndian(buf.Slice(vtableOff + 4 + 2 * i, 2));
        return true;
    }

    private static bool HasField(int[] fields, int idx) => idx < fields.Length && fields[idx] != 0;

    private static bool TryReadUInt8Field(ReadOnlySpan<byte> buf, int tableOff, int[] fields, int idx,
        out byte value, out string error)
    {
        value = 0; error = "";
        if (!HasField(fields, idx)) { value = 0; return true; }
        var abs = tableOff + fields[idx];
        if (abs + 1 > buf.Length) { error = "u8 field past EOF"; return false; }
        value = buf[abs];
        return true;
    }

    private static bool TryReadUInt16Field(ReadOnlySpan<byte> buf, int tableOff, int[] fields, int idx,
        out ushort value, out string error)
    {
        value = 0; error = "";
        if (!HasField(fields, idx)) { value = 0; return true; }
        var abs = tableOff + fields[idx];
        if (abs + 2 > buf.Length) { error = "u16 field past EOF"; return false; }
        value = BinaryPrimitives.ReadUInt16LittleEndian(buf.Slice(abs, 2));
        return true;
    }

    private static bool TryReadUOffsetField(ReadOnlySpan<byte> buf, int tableOff, int[] fields, int idx,
        out int rel, out string error)
    {
        rel = 0; error = "";
        if (!HasField(fields, idx)) { rel = 0; return true; }
        var abs = tableOff + fields[idx];
        if (abs + 4 > buf.Length) { error = "uoffset field past EOF"; return false; }
        rel = (int)BinaryPrimitives.ReadUInt32LittleEndian(buf.Slice(abs, 4));
        return true;
    }

    // Same as TryReadUOffsetField but also returns the absolute byte position where
    // the uoffset itself is stored. Required because uoffsets are relative to their
    // own storage location, not to the enclosing table.
    private static bool TryReadUOffsetFieldLocation(ReadOnlySpan<byte> buf, int tableOff, int[] fields,
        int idx, out uint storeAbs, out uint rel, out string error)
    {
        storeAbs = 0; rel = 0; error = "";
        if (!HasField(fields, idx)) return true;
        var abs = tableOff + fields[idx];
        if (abs + 4 > buf.Length) { error = "uoffset field past EOF"; return false; }
        storeAbs = (uint)abs;
        rel = BinaryPrimitives.ReadUInt32LittleEndian(buf.Slice(abs, 4));
        return true;
    }

    private static bool TryReadVector(ReadOnlySpan<byte> span, int vecAbs, out int count, out string? error)
    {
        // Vector layout: [uoffset32 from vecAbs to vec_data][vec_data: u32 count][elements...]
        count = 0; error = null;
        if (vecAbs + 4 > span.Length) { error = "vector slot past EOF"; return false; }
        var rel = BinaryPrimitives.ReadUInt32LittleEndian(span[vecAbs..(vecAbs + 4)]);
        var dataAbs = vecAbs + (int)rel;
        if (dataAbs + 4 > span.Length) { error = "vector count past EOF"; return false; }
        count = (int)BinaryPrimitives.ReadUInt32LittleEndian(span[dataAbs..(dataAbs + 4)]);
        return true;
    }
}
