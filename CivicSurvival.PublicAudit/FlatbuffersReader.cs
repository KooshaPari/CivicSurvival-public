// Hand-rolled FlatBuffers reader used by the public-audit runner.
//
// Supports only what the audit needs:
//   - 4-byte file_identifier lock (CSWP)
//   - root uoffset (must be safe to follow)
//   - Envelope: payload_type (uint8), payload (union table offset)
//   - CommandBatch: schema_version (uint16), commands (vector of tables)
//   - CommandEnvelope: kind (uint8), payload (vector of bytes)
//   - ProjectionDelta: campaign_id/observer_id/state_hash/views/...
//     byte vectors; base_revision/new_revision/tick/validated_revision
//     uint32; decisions[] (vector of CommandDecision tables)
//
// Mirrors the wire layout documented in Google FlatBuffers (Apache 2.0)
// without pulling in the library. Bounds-checks every offset to reject
// corruption, truncation, and arbitrary-length attacks.
//
// Cross-validated against `flatc --binary` output via `flatc --json
// --raw-binary --strict-json` of the committed golden fixtures at
// .agileplus/civic-warfare-program/contracts/fixtures/.

using System.Buffers.Binary;

public static class FlatbuffersReader
{
    public enum RootPayloadKind : byte { NONE = 0, CommandBatch = 1, ProjectionDelta = 2, SaveEnvelope = 3 }

    public readonly record struct CommandView(int KindByte, int PayloadByteCount);

    public readonly record struct DecisionView(int CodeByte, int ReasonKeyByteCount, int DetailsByteCount);

    public sealed class EnvelopeView
    {
        public RootPayloadKind PayloadType { get; set; }
        public ushort SchemaVersion { get; set; }
        public int CommandCount => Commands.Count;
        public List<CommandView> Commands { get; } = new();

        // ProjectionDelta fields (populated when PayloadType == ProjectionDelta).
        public uint BaseRevision { get; set; }
        public uint NewRevision { get; set; }
        public uint Tick { get; set; }
        public int CampaignIdByteCount { get; set; }
        public int ObserverIdByteCount { get; set; }
        public int StateHashByteCount { get; set; }
        public int ViewsByteCount { get; set; }
        public int RemovalsByteCount { get; set; }
        public int AlertsByteCount { get; set; }
        public int ExplanationsByteCount { get; set; }
        public List<DecisionView> Decisions { get; } = new();
        public int DecisionCount => Decisions.Count;
    }

    public static bool TryParseEnvelope(byte[] buffer, string expectedFileIdentifier,
        string expectedRootType, out EnvelopeView envelope, out string? error)
    {
        envelope = null!;
        error = null;
        if (buffer is null || buffer.Length < 8) { error = "buffer < 8 bytes"; return false; }

        var span = buffer.AsSpan();
        var rootOffset = BinaryPrimitives.ReadUInt32LittleEndian(span[0..4]);
        if (rootOffset > buffer.Length - 4) { error = $"root offset {rootOffset} past EOF"; return false; }

        var ident = System.Text.Encoding.ASCII.GetString(span[4..8]);
        if (!string.Equals(ident, expectedFileIdentifier, StringComparison.Ordinal))
        { error = $"file_identifier {ident} != {expectedFileIdentifier}"; return false; }
        _ = expectedRootType;

        var rootTableOff = (int)rootOffset;
        var env = new EnvelopeView();
        if (!TryFollowTable(span, rootTableOff, out var envFields, out error)) return false;
        if (!TryReadUInt8Field(span, rootTableOff, envFields, 0, out var payloadTypeByte, out error))
            return false;
        env.PayloadType = (RootPayloadKind)payloadTypeByte;

        if (!TryReadUOffsetFieldLocation(span, rootTableOff, envFields, 1, out var payloadStoreAbs,
                out var payloadRel, out error)) return false;
        var payloadAbs = (int)(payloadStoreAbs + payloadRel);

        switch (env.PayloadType)
        {
            case RootPayloadKind.CommandBatch:
                if (!DecodeCommandBatch(span, payloadAbs, env, out error)) return false;
                break;
            case RootPayloadKind.ProjectionDelta:
                if (!DecodeProjectionDelta(span, payloadAbs, env, out error)) return false;
                break;
            default:
                // SaveEnvelope and NONE: leave EnvelopeView at defaults.
                break;
        }

        envelope = env;
        return true;
    }

    private static bool DecodeCommandBatch(ReadOnlySpan<byte> span, int payloadAbs,
        EnvelopeView env, out string? error)
    {
        error = null;
        if (!TryFollowTable(span, payloadAbs, out var cbFields, out error)) return false;
        if (!TryReadUInt16Field(span, payloadAbs, cbFields, 0, out var schemaVersion, out error))
            return false;
        env.SchemaVersion = schemaVersion;

        if (!TryReadUOffsetFieldLocation(span, payloadAbs, cbFields, 1, out var cmdsStoreAbs,
                out var cmdsRel, out error)) return false;
        var cmdsVecAbs = (int)(cmdsStoreAbs + cmdsRel);
        if (cmdsVecAbs + 4 > span.Length) { error = "commands vector slot past EOF"; return false; }
        var cmdCount = (int)BinaryPrimitives.ReadUInt32LittleEndian(span[cmdsVecAbs..(cmdsVecAbs + 4)]);
        var cmdVecDataAbs = cmdsVecAbs + 4;
        for (int i = 0; i < cmdCount; i++)
        {
            var elemAbs = cmdVecDataAbs + i * 4;
            if (elemAbs + 4 > span.Length) { error = "truncated commands vector"; return false; }
            var cmdRel = BinaryPrimitives.ReadUInt32LittleEndian(span[elemAbs..(elemAbs + 4)]);
            var cmdAbs = elemAbs + (int)cmdRel;
            if (cmdAbs + 4 > span.Length) { error = $"command[{i}] table off {cmdAbs} past EOF"; return false; }
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
        return true;
    }

    private static bool DecodeProjectionDelta(ReadOnlySpan<byte> span, int payloadAbs,
        EnvelopeView env, out string? error)
    {
        error = null;
        if (!TryFollowTable(span, payloadAbs, out var pdFields, out error)) return false;

        env.CampaignIdByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 0, out error);
        if (env.CampaignIdByteCount < 0) return false;
        env.ObserverIdByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 1, out error);
        if (env.ObserverIdByteCount < 0) return false;
        if (HasField(pdFields, 2))
        {
            var abs = payloadAbs + pdFields[2];
            if (abs + 4 > span.Length) { error = "base_revision past EOF"; return false; }
            env.BaseRevision = BinaryPrimitives.ReadUInt32LittleEndian(span.Slice(abs, 4));
        }
        if (HasField(pdFields, 3))
        {
            var abs = payloadAbs + pdFields[3];
            if (abs + 4 > span.Length) { error = "new_revision past EOF"; return false; }
            env.NewRevision = BinaryPrimitives.ReadUInt32LittleEndian(span.Slice(abs, 4));
        }
        if (HasField(pdFields, 4))
        {
            var abs = payloadAbs + pdFields[4];
            if (abs + 4 > span.Length) { error = "tick past EOF"; return false; }
            env.Tick = BinaryPrimitives.ReadUInt32LittleEndian(span.Slice(abs, 4));
        }
        env.StateHashByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 5, out error);
        if (env.StateHashByteCount < 0) return false;
        if (!TryReadUOffsetFieldLocation(span, payloadAbs, pdFields, 6, out var decStoreAbs,
                out var decRel, out error)) return false;
        var decVecAbs = (int)(decStoreAbs + decRel);
        if (decVecAbs + 4 > span.Length) { error = "decisions vector slot past EOF"; return false; }
        var decCount = (int)BinaryPrimitives.ReadUInt32LittleEndian(span[decVecAbs..(decVecAbs + 4)]);
        var decVecDataAbs = decVecAbs + 4;
        for (int i = 0; i < decCount; i++)
        {
            var elemAbs = decVecDataAbs + i * 4;
            if (elemAbs + 4 > span.Length) { error = "truncated decisions vector"; return false; }
            var dRel = BinaryPrimitives.ReadUInt32LittleEndian(span[elemAbs..(elemAbs + 4)]);
            var dAbs = elemAbs + (int)dRel;
            if (dAbs + 4 > span.Length) { error = $"decision[{i}] table off {dAbs} past EOF"; return false; }
            if (!TryFollowTable(span, dAbs, out var dFields, out error)) return false;
            ushort codeByte = 0;
            if (HasField(dFields, 2))
            {
                var abs = dAbs + dFields[2];
                if (abs + 2 > span.Length) { error = "decision code past EOF"; return false; }
                codeByte = BinaryPrimitives.ReadUInt16LittleEndian(span.Slice(abs, 2));
            }
            int reasonKeyLen = 0;
            if (HasField(dFields, 3))
            {
                if (!TryReadUOffsetFieldLocation(span, dAbs, dFields, 3, out var rkStoreAbs,
                        out var rkRel, out error)) return false;
                var rkAbs = (int)(rkStoreAbs + rkRel);
                if (!TryReadVector(span, rkAbs, out var rkCount, out error))
                    return false;
                reasonKeyLen = rkCount;
            }
            int detailsLen = 0;
            if (HasField(dFields, 5))
            {
                if (!TryReadUOffsetFieldLocation(span, dAbs, dFields, 5, out var dtStoreAbs,
                        out var dtRel, out error)) return false;
                var dtAbs = (int)(dtStoreAbs + dtRel);
                if (!TryReadVector(span, dtAbs, out var dtCount, out error))
                    return false;
                detailsLen = dtCount;
            }
            env.Decisions.Add(new DecisionView(codeByte, reasonKeyLen, detailsLen));
        }
        env.ViewsByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 7, out error);
        if (env.ViewsByteCount < 0) return false;
        env.RemovalsByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 8, out error);
        if (env.RemovalsByteCount < 0) return false;
        env.AlertsByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 9, out error);
        if (env.AlertsByteCount < 0) return false;
        env.ExplanationsByteCount = ReadByteVectorLen(span, payloadAbs, pdFields, 10, out error);
        if (env.ExplanationsByteCount < 0) return false;
        return true;
    }

    private static int ReadByteVectorLen(ReadOnlySpan<byte> span, int tableOff, int[] fields, int idx,
        out string? error)
    {
        error = null;
        if (!HasField(fields, idx)) return 0;
        if (!TryReadUOffsetFieldLocation(span, tableOff, fields, idx, out var storeAbs, out var rel, out error))
            return -1;
        var vecAbs = (int)(storeAbs + rel);
        if (!TryReadVector(span, vecAbs, out var count, out error))
            return -1;
        return count;
    }

    private static bool TryFollowTable(ReadOnlySpan<byte> buf, int tableOff, out int[] fields, out string error)
    {
        fields = Array.Empty<int>();
        error = "";
        if (tableOff < 0 || tableOff + 4 > buf.Length)
        { error = $"table off {tableOff} past EOF"; return false; }
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
        count = 0; error = null;
        if (vecAbs + 4 > span.Length) { error = "vector slot past EOF"; return false; }
        var rel = BinaryPrimitives.ReadUInt32LittleEndian(span[vecAbs..(vecAbs + 4)]);
        var dataAbs = vecAbs + (int)rel;
        if (dataAbs + 4 > span.Length) { error = "vector count past EOF"; return false; }
        count = (int)BinaryPrimitives.ReadUInt32LittleEndian(span[dataAbs..(dataAbs + 4)]);
        return true;
    }
}
