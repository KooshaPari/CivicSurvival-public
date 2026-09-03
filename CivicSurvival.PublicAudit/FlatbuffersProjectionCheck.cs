// WP02-C 7th public-audit gate — invokes the Python reader as a
// subprocess and cross-validates its output against canonical flatc
// values for the ProjectionDelta golden fixture (sample-projection.bin).
//
// The Python reader was extended in WP02-C to decode all 3 RootPayload
// union arms; this gate exercises the ProjectionDelta arm.

using System.Diagnostics;
using System.Text.Json;

namespace CivicSurvival.PublicAudit;

public static class FlatbuffersProjectionCheck
{
    public static bool CheckFlatbuffersProjection(string repoRoot, out string? error)
    {
        error = null;
        var fixture = Path.Combine(
            repoRoot,
            ".agileplus/civic-warfare-program/contracts/fixtures/sample-projection.bin");
        var readerScript = Path.Combine(repoRoot, "tests/flatbuffers_reader.py");

        if (!File.Exists(fixture))
        {
            error = $"projection fixture not found: {fixture}";
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
    'base_revision': payload['base_revision'],
    'new_revision': payload['new_revision'],
    'tick': payload['tick'],
    'decisions_count': len(payload['decisions']),
    'decision_codes': [d['code'] for d in payload['decisions']],
    'decision_reasons': [d['reason_key'] for d in payload['decisions']],
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

        if (root.GetProperty("payload_type").GetString() != "ProjectionDelta")
        {
            error = $"python reader payload_type != ProjectionDelta (got {root.GetProperty("payload_type").GetString()})";
            return false;
        }
        if (root.GetProperty("base_revision").GetInt32() != 100)
        {
            error = $"python reader base_revision != 100 (got {root.GetProperty("base_revision").GetInt32()})";
            return false;
        }
        if (root.GetProperty("new_revision").GetInt32() != 101)
        {
            error = $"python reader new_revision != 101 (got {root.GetProperty("new_revision").GetInt32()})";
            return false;
        }
        if (root.GetProperty("tick").GetInt32() != 500)
        {
            error = $"python reader tick != 500 (got {root.GetProperty("tick").GetInt32()})";
            return false;
        }
        if (root.GetProperty("decisions_count").GetInt32() != 2)
        {
            error = $"python reader decisions_count != 2 (got {root.GetProperty("decisions_count").GetInt32()})";
            return false;
        }
        var codes = root.GetProperty("decision_codes").EnumerateArray().Select(e => e.GetString()).ToArray();
        if (codes.Length != 2 || codes[0] != "Accepted" || codes[1] != "InsufficientResources")
        {
            error = $"python reader decision_codes != [Accepted, InsufficientResources] (got [{string.Join(", ", codes)}])";
            return false;
        }
        var reasons = root.GetProperty("decision_reasons").EnumerateArray().Select(e => e.GetString()).ToArray();
        if (reasons.Length != 2 || reasons[0] != "ok" || reasons[1] != "low_fuel")
        {
            error = $"python reader decision_reasons != [ok, low_fuel] (got [{string.Join(", ", reasons)}])";
            return false;
        }

        return true;
    }

    private static string QuotePath(string p) => "\"" + p.Replace("\"", "\\\"") + "\"";
}
