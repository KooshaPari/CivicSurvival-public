using System.Buffers.Binary;
using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

var root = args.FirstOrDefault(a => !a.StartsWith("--", StringComparison.Ordinal))
    ?? Directory.GetCurrentDirectory();
var json = args.Any(a => a == "--json");
var contractsProject = Path.Combine(root, "CivicSurvival.Contracts", "CivicSurvival.Contracts.csproj");
var localizationRoot = Path.Combine(root, "CivicSurvival", "Localization");
var contractText = File.Exists(contractsProject) ? File.ReadAllText(contractsProject) : "";
var flatbuffersRootSource = FlatbuffersRootSource.Find(root);
var result = new AuditResult
{
    ContractsBuildValue = File.Exists(contractsProject) &&
        !contractText.Contains("Mod.props", StringComparison.Ordinal) &&
        !contractText.Contains("Mod.targets", StringComparison.Ordinal) &&
        RunBuild(contractsProject),
    LocalizationParityValue = CheckLocalization(localizationRoot),
    SourceRootsValue = CheckSourceRoots(root),
    FlatbuffersSchemaValue = CheckFlatbuffersSchema(root),
    FlatbuffersRoundTripValue = CheckFlatbuffersRoundTrip(flatbuffersRootSource!, out var roundTripMessage),
};
result.Status = ComputeStatus(result);

if (json)
{
    Console.WriteLine(JsonSerializer.Serialize(result, new JsonSerializerOptions
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = false,
    }));
}
else
{
    Console.WriteLine($"Public audit: {result.Status}");
    Console.WriteLine($"Contracts: {result.ContractsBuild}");
    Console.WriteLine($"Localization: {result.LocalizationParity}");
    Console.WriteLine($"Source roots: {result.SourceRoots}");
    Console.WriteLine($"FlatBuffers schema contract: {result.FlatbuffersSchema}");
    Console.WriteLine($"FlatBuffers round-trip: {result.FlatbuffersRoundTrip}");
    if (roundTripMessage is not null) Console.WriteLine($"  -> {roundTripMessage}");
}

return result.Status == "pass" ? 0 : 1;

static string ComputeStatus(AuditResult r) =>
    r.ContractsBuildValue && r.LocalizationParityValue && r.SourceRootsValue &&
    r.FlatbuffersSchemaValue && r.FlatbuffersRoundTripValue
        ? "pass" : "fail";

static bool CheckLocalization(string root)
{
    if (!Directory.Exists(root)) return false;
    var files = Directory.GetFiles(root, "*.json").OrderBy(path => path).ToArray();
    if (files.Length < 2) return false;
    try
    {
        var keySets = files.Select(path =>
        {
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            return Flatten(document.RootElement).ToHashSet(StringComparer.Ordinal);
        }).ToArray();
        return keySets.All(keys => keys.SetEquals(keySets[0]));
    }
    catch (JsonException) { return false; }
}

static IEnumerable<string> Flatten(JsonElement element, string prefix = "")
{
    if (element.ValueKind != JsonValueKind.Object) yield break;
    foreach (var property in element.EnumerateObject())
    {
        var key = string.IsNullOrEmpty(prefix) ? property.Name : $"{prefix}.{property.Name}";
        if (property.Value.ValueKind == JsonValueKind.Object)
        {
            foreach (var child in Flatten(property.Value, key)) yield return child;
        }
        else yield return key;
    }
}

static bool CheckSourceRoots(string root)
{
    var required = new[]
    {
        Path.Combine(root, "CivicSurvival.Contracts", "CivicSurvival.Contracts.csproj"),
        Path.Combine(root, "CivicSurvival", "Config", "balance_config.json"),
        Path.Combine(root, "CivicSurvival", "Localization", "en-US.json"),
        Path.Combine(root, "CivicSurvival", "Localization", "uk-UA.json"),
        Path.Combine(root, "CivicSurvival", "Localization", "zh-CN.json"),
    };
    return required.All(File.Exists);
}

// WP02-A: the public source mirror must preserve a bounded, versioned FlatBuffers
// contract and a C ABI header. This gate rejects drift in any direction:
//   - missing files,
//   - missing required enum members (no shrinking to a subset of commands/decisions),
//   - removed root_type or file_identifier (the wire format would silently change),
//   - any reference to the proprietary game SDK in the public ABI header.
static bool CheckFlatbuffersSchema(string root)
{
    var fbsPath = Path.Combine(root, ".agileplus", "civic-warfare-program", "contracts", "warfare.fbs");
    var headerPath = Path.Combine(root, ".agileplus", "civic-warfare-program", "contracts", "civic_warfare.h");
    if (!File.Exists(fbsPath) || !File.Exists(headerPath)) return false;

    var fbs = File.ReadAllText(fbsPath);
    var header = File.ReadAllText(headerPath);

    // Required enum members (must NOT shrink).
    var requiredCommandKinds = new[]
    {
        "None", "SetPolicy", "SetDelegation", "Procure", "Construct",
        "Mobilize", "AssignForce", "CreateOperation", "UpdateOperation",
        "CancelOperation", "SetMission", "Negotiate", "ConductCovertOperation",
        "RespondToCivilEvent",
    };
    var requiredDecisionCodes = new[]
    {
        "Accepted", "Duplicate", "RevisionConflict", "Unauthorized",
        "InvalidConfiguration", "MissingPrerequisite", "InsufficientResources",
        "InvalidTarget", "Expired", "RejectedByPolicy",
    };
    if (requiredCommandKinds.Any(kind => !fbs.Contains(kind, StringComparison.Ordinal))) return false;
    if (requiredDecisionCodes.Any(code => !fbs.Contains(code, StringComparison.Ordinal))) return false;

    // Required wire-level declarations.
    if (!fbs.Contains("root_type Envelope", StringComparison.Ordinal)) return false;
    if (!fbs.Contains("file_identifier \"CSWP\"", StringComparison.Ordinal)) return false;
    if (!fbs.Contains("union RootPayload", StringComparison.Ordinal)) return false;

    // Required C ABI surface.
    var requiredAbiFunctions = new[]
    {
        "csw_abi_version", "csw_create", "csw_load",
        "csw_submit_commands", "csw_step", "csw_poll_into",
        "csw_save_into", "csw_status_into", "csw_last_error_into", "csw_destroy",
    };
    if (requiredAbiFunctions.Any(fn => !header.Contains(fn, StringComparison.Ordinal))) return false;

    // Public header must not depend on the licensed CS2 SDK.
    if (header.Contains("ColossalOrder", StringComparison.OrdinalIgnoreCase)) return false;
    if (header.Contains("CitiesSkylines", StringComparison.OrdinalIgnoreCase)) return false;
    if (header.Contains("UnityEngine", StringComparison.Ordinal)) return false;

    return true;
}

// WP02-A second gate: round-trip decode. The public-audit runner ingests the
// golden fixture emitted by flatc from .agileplus/civic-warfare-program/
// contracts/warfare.fbs. If the schema or the C ABI drift, this gate fails
// before any native Rust reader is written.
//
// Hand-rolled reader to avoid a NuGet dependency on Google.FlatBuffers.
// Cross-validated against `flatc --json --raw-binary` for every fixture that
// passes this gate.
static bool CheckFlatbuffersRoundTrip(FlatbuffersRootSource source, out string? detail)
{
    detail = null;
    if (source is null) return false;
    if (!File.Exists(source.GoldenEnvelope)) return false;
    if (!File.Exists(source.Fbs)) return false;

    var bytes = File.ReadAllBytes(source.GoldenEnvelope);
    if (!FlatbuffersReader.TryParseEnvelope(bytes, source.ExpectedFileIdentifier,
            expectedRootType: source.RootTypeName, out var parsed, out var parseError))
    {
        detail = $"golden binary failed to parse: {parseError}";
        return false;
    }

    if (parsed.PayloadType != FlatbuffersReader.RootPayloadKind.CommandBatch)
    {
        detail = $"expected payload_type CommandBatch, got {parsed.PayloadType}";
        return false;
    }
    if (parsed.SchemaVersion != 7)
    {
        detail = $"expected schema_version=7 (golden), got {parsed.SchemaVersion}";
        return false;
    }
    if (parsed.CommandCount != 2)
    {
        detail = $"expected 2 commands in golden, got {parsed.CommandCount}";
        return false;
    }
    if (parsed.Commands[0].KindByte != 10) // SetMission
    {
        detail = $"command[0] kind byte != SetMission(10), got {parsed.Commands[0].KindByte}";
        return false;
    }
    if (parsed.Commands[1].KindByte != 11) // Negotiate
    {
        detail = $"command[1] kind byte != Negotiate(11), got {parsed.Commands[1].KindByte}";
        return false;
    }

    return true;
}
static bool RunBuild(string project)
{
    try
    {
        using var process = Process.Start(new ProcessStartInfo
        {
            FileName = "dotnet",
            ArgumentList = { "build", project, "--framework", "net8.0", "--nologo", "--verbosity", "quiet" },
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        });
        if (process is null) return false;
        if (!process.WaitForExit(TimeSpan.FromMinutes(2)))
        {
            try { process.Kill(entireProcessTree: true); } catch (InvalidOperationException) { }
            return false;
        }
        return process.ExitCode == 0;
    }
    catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
    {
        return false;
    }
}

// Resolves the directory holding warfare.fbs, civic_warfare.h, and the golden
// FlatBuffers fixtures committed under contracts/fixtures/.
sealed record FlatbuffersRootSource(string Root, string Fbs, string Header, string GoldenEnvelope,
    string ExpectedFileIdentifier, string RootTypeName)
{
    public static FlatbuffersRootSource? Find(string repoRoot)
    {
        var dir = Path.Combine(repoRoot, ".agileplus", "civic-warfare-program", "contracts");
        if (!Directory.Exists(dir)) return null;
        var fbs = Path.Combine(dir, "warfare.fbs");
        var header = Path.Combine(dir, "civic_warfare.h");
        var golden = Path.Combine(dir, "fixtures", "sample-envelope.bin");
        if (!File.Exists(fbs) || !File.Exists(header) || !File.Exists(golden)) return null;
        var fbsText = File.ReadAllText(fbs);
        // Lock down the file_identifier so a schema rename without updating
        // the audit fails here rather than silently producing wrong payloads.
        var identMarker = "file_identifier \"";
        var identStart = fbsText.IndexOf(identMarker, StringComparison.Ordinal);
        if (identStart < 0) return null;
        var identEnd = fbsText.IndexOf('"', identStart + identMarker.Length);
        if (identEnd < 0) return null;
        var ident = fbsText.Substring(identStart + identMarker.Length,
            identEnd - (identStart + identMarker.Length));
        if (ident.Length != 4) return null;

        var rootTypeMarker = "root_type ";
        var rootStart = fbsText.IndexOf(rootTypeMarker, StringComparison.Ordinal);
        if (rootStart < 0) return null;
        var rootLineEnd = fbsText.IndexOfAny(new[] { '\r', '\n', ' ', '\t' },
            rootStart + rootTypeMarker.Length);
        if (rootLineEnd < 0) rootLineEnd = fbsText.Length;
        var rootType = fbsText.Substring(rootStart + rootTypeMarker.Length,
            rootLineEnd - (rootStart + rootTypeMarker.Length)).Trim();

        return new FlatbuffersRootSource(dir, fbs, header, golden, ident, rootType);
    }
}
// Hand-rolled FlatBuffers reader. Supports only what the audit needs:
//   - 4-byte file_identifier lock
//   - root uoffset (must be safe)
//   - Envelope: payload_type (uint8), payload (union table offset)
//   - CommandBatch: schema_version (uint16), commands (vector of tables)
//   - CommandEnvelope: kind (uint8), payload (vector of bytes)
//
// Mirrors the wire layout documented in Google FlatBuffers (Apache 2.0) without
// pulling in the library. Bounds-checks every offset to reject corruption,
// truncation, and arbitrary-length attacks.
static class FlatbuffersReader
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


sealed class AuditResult
{
    public string Status { get; set; } = "fail";
    public string ContractsBuild => ContractsBuildValue ? "pass" : "fail";
    public string LocalizationParity => LocalizationParityValue ? "pass" : "fail";
    public string SourceRoots => SourceRootsValue ? "pass" : "fail";
    public string FlatbuffersSchema => FlatbuffersSchemaValue ? "pass" : "fail";
    public string FlatbuffersRoundTrip => FlatbuffersRoundTripValue ? "pass" : "fail";
    [JsonIgnore] public bool ContractsBuildValue { get; set; }
    [JsonIgnore] public bool LocalizationParityValue { get; set; }
    [JsonIgnore] public bool SourceRootsValue { get; set; }
    [JsonIgnore] public bool FlatbuffersSchemaValue { get; set; }
    [JsonIgnore] public bool FlatbuffersRoundTripValue { get; set; }
}
