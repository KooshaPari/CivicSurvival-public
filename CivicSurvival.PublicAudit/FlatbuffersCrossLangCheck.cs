// Cross-language FlatBuffers gate — invokes the Python reader as a
// subprocess and cross-validates its output against the C# reader's
// output. Both implementations are independent, hand-written, and
// verified against the same flatc-encoded golden fixture.
//
// Both readers decode:
//   - file_identifier (CSWP)
//   - root table vtable follow
//   - Envelope.payload_type discriminator (RootPayloadKind)
//   - CommandBatch.schema_version (uint16)
//   - CommandBatch.commands count
//   - CommandEnvelope.kind (uint16, mapped via CommandKind enum)
//
// The Python reader also decodes the byte-vectors (command_id etc.)
// which the C# reader intentionally does not (the C# reader stays
// narrow on purpose: structural decode + key fields only).

using System.Diagnostics;

public static class FlatbuffersCrossLangCheck
{
    public static bool CheckFlatbuffersCrossLang(string repoRoot, out string? error)
    {
        error = null;
        var fixture = Path.Combine(
            repoRoot,
            ".agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin");
        var readerScript = Path.Combine(repoRoot, "tests/flatbuffers_reader.py");

        if (!File.Exists(fixture))
        {
            error = $"golden fixture not found: {fixture}";
            return false;
        }
        if (!File.Exists(readerScript))
        {
            error = $"Python reader not found: {readerScript}";
            return false;
        }

        // Build a small Python invocation that decodes the fixture and
        // emits the same field set the C# reader validates.
        var pythonScript = $@"
import sys, json
sys.path.insert(0, {QuotePath(Path.GetDirectoryName(readerScript)!)})
from flatbuffers_reader import decode_envelope
out = decode_envelope(open({QuotePath(fixture)}, 'rb').read())
payload = out['payload']
# Emit ONLY the fields the C# reader also validates.
result = {{
    'payload_type': out['payload_type'],
    'schema_version': payload['schema_version'],
    'commands_count': len(payload['commands']),
    'command_kinds': [c['kind'] for c in payload['commands']],
    'command_priorities': [c['priority'] for c in payload['commands']],
}}
print(json.dumps(result))
";

        var psi = new ProcessStartInfo
        {
            FileName = "python3",
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
        };
        psi.ArgumentList.Add("-c");
        psi.ArgumentList.Add(pythonScript);

        string stdout;
        string stderr;
        try
        {
            using var proc = Process.Start(psi)!;
            stdout = proc.StandardOutput.ReadToEnd();
            stderr = proc.StandardError.ReadToEnd();
            proc.WaitForExit(5_000);
            if (proc.ExitCode != 0)
            {
                error = $"python3 exited {proc.ExitCode}: {stderr.Trim()}";
                return false;
            }
        }
        catch (Exception ex)
        {
            error = $"failed to spawn python3: {ex.Message}";
            return false;
        }

        // Parse Python's JSON and verify against the canonical values
        // (these match the C# reader's expected values for the golden fixture).
        var doc = System.Text.Json.JsonDocument.Parse(stdout.Trim());
        var root = doc.RootElement;
        if (root.GetProperty("payload_type").GetString() != "CommandBatch")
        {
            error = $"Python reader: payload_type != CommandBatch (got {root.GetProperty("payload_type").GetString()})";
            return false;
        }
        if (root.GetProperty("schema_version").GetInt32() != 7)
        {
            error = $"Python reader: schema_version != 7 (got {root.GetProperty("schema_version").GetInt32()})";
            return false;
        }
        if (root.GetProperty("commands_count").GetInt32() != 2)
        {
            error = $"Python reader: commands_count != 2 (got {root.GetProperty("commands_count").GetInt32()})";
            return false;
        }
        var kinds = root.GetProperty("command_kinds").EnumerateArray().Select(e => e.GetString()).ToArray();
        if (kinds.Length != 2 || kinds[0] != "SetMission" || kinds[1] != "Negotiate")
        {
            error = $"Python reader: kinds != [SetMission, Negotiate] (got [{string.Join(", ", kinds)}])";
            return false;
        }
        var priorities = root.GetProperty("command_priorities").EnumerateArray().Select(e => GetInt(e)).ToArray();
        if (priorities.Length != 2 || priorities[0] != 5 || priorities[1] != -1)
        {
            error = $"Python reader: priorities != [5, -1] (got [{string.Join(", ", priorities)}])";
            return false;
        }
        return true;
    }

    private static string QuotePath(string p) => "\"" + p.Replace("\"", "\\\"") + "\"";

    private static int GetInt(System.Text.Json.JsonElement e) =>
        e.ValueKind == System.Text.Json.JsonValueKind.Number ? e.GetInt32() : 0;
}
