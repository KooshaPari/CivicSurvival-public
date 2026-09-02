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
var result = new AuditResult
{
    ContractsBuildValue = File.Exists(contractsProject) &&
        !contractText.Contains("Mod.props", StringComparison.Ordinal) &&
        !contractText.Contains("Mod.targets", StringComparison.Ordinal) &&
        RunBuild(contractsProject),
    LocalizationParityValue = CheckLocalization(localizationRoot),
    SourceRootsValue = CheckSourceRoots(root),
    FlatbuffersSchemaValue = CheckFlatbuffersSchema(root),
};
result.Status = result.ContractsBuildValue && result.LocalizationParityValue && result.SourceRootsValue && result.FlatbuffersSchemaValue ? "pass" : "fail";

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
    Console.WriteLine($"Contracts: {(result.ContractsBuildValue ? "pass" : "fail")}");
    Console.WriteLine($"Localization: {(result.LocalizationParityValue ? "pass" : "fail")}");
    Console.WriteLine($"Source roots: {(result.SourceRootsValue ? "pass" : "fail")}");
    Console.WriteLine($"FlatBuffers schema contract: {(result.FlatbuffersSchemaValue ? "pass" : "fail")}");
}

return result.Status == "pass" ? 0 : 1;

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

sealed class AuditResult
{
    public string Status { get; set; } = "fail";
    public string ContractsBuild => ContractsBuildValue ? "pass" : "fail";
    public string LocalizationParity => LocalizationParityValue ? "pass" : "fail";
    public string SourceRoots => SourceRootsValue ? "pass" : "fail";
    public string FlatbuffersSchema => FlatbuffersSchemaValue ? "pass" : "fail";
    [JsonIgnore] public bool ContractsBuildValue { get; set; }
    [JsonIgnore] public bool LocalizationParityValue { get; set; }
    [JsonIgnore] public bool SourceRootsValue { get; set; }
    [JsonIgnore] public bool FlatbuffersSchemaValue { get; set; }
}
