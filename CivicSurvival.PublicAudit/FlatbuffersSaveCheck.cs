// WP02-D 8th public-audit gate — invokes the Python reader as a
// subprocess and cross-validates its output against canonical flatc
// values for the SaveEnvelope golden fixture (sample-save.bin).
//
// The Python reader was extended in WP02-D to decode all 3 RootPayload
// union arms; this gate exercises the SaveEnvelope arm.

using System.Diagnostics;
using System.Text.Json;

namespace CivicSurvival.PublicAudit;

public static class FlatbuffersSaveCheck
{
    public static bool CheckFlatbuffersSave(string repoRoot, out string? error)
    {
        error = null;
        var fixture = Path.Combine(
            repoRoot,
            ".agileplus/civic-warfare-program/contracts/fixtures/sample-save.bin");
        var readerScript = Path.Combine(repoRoot, "tests/flatbuffers_reader.py");

        if (!File.Exists(fixture))
        {
            error = $"save fixture not found: {fixture}";
            return false;
        }
        if (!File.Exists(readerScript))
        {
            error = $"Python reader not found: {readerScript}";
            return false;
        }

        var pythonScript = $@"
import sys, json
sys.path.insert(0, {QuotePath(Path.GetDirectoryName(readerScript)!)})
from flatbuffers_reader import decode_envelope
out = decode_envelope(open({QuotePath(fixture)}, 'rb').read())
payload = out['payload']
result = {{
    'payload_type': out['payload_type'],
    'abi_version': payload['abi_version'],
    'schema_version': payload['schema_version'],
    'save_version': payload['save_version'],
    'rng_version': payload['rng_version'],
    'tick': payload['tick'],
    'revision': payload['revision'],
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

        var doc = JsonDocument.Parse(stdout.Trim());
        var root = doc.RootElement;

        if (root.GetProperty("payload_type").GetString() != "SaveEnvelope")
        {
            error = $"python reader payload_type != SaveEnvelope (got {root.GetProperty("payload_type").GetString()})";
            return false;
        }
        if (root.GetProperty("abi_version").GetInt32() != 1)
        {
            error = $"python reader abi_version != 1 (got {root.GetProperty("abi_version").GetInt32()})";
            return false;
        }
        if (root.GetProperty("schema_version").GetInt32() != 7)
        {
            error = $"python reader schema_version != 7 (got {root.GetProperty("schema_version").GetInt32()})";
            return false;
        }
        if (root.GetProperty("save_version").GetInt32() != 42)
        {
            error = $"python reader save_version != 42 (got {root.GetProperty("save_version").GetInt32()})";
            return false;
        }
        if (root.GetProperty("rng_version").GetInt32() != 100)
        {
            error = $"python reader rng_version != 100 (got {root.GetProperty("rng_version").GetInt32()})";
            return false;
        }
        if (root.GetProperty("tick").GetInt64() != 1234567890L)
        {
            error = $"python reader tick != 1234567890 (got {root.GetProperty("tick").GetInt64()})";
            return false;
        }
        if (root.GetProperty("revision").GetInt64() != 98765L)
        {
            error = $"python reader revision != 98765 (got {root.GetProperty("revision").GetInt64()})";
            return false;
        }

        return true;
    }

    private static string QuotePath(string p) => "\"" + p.Replace("\"", "\\\"") + "\"";
}
