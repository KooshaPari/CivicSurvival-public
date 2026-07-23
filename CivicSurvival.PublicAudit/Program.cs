using System.Diagnostics;
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
};
result.Status = result.ContractsBuildValue && result.LocalizationParityValue && result.SourceRootsValue ? "pass" : "fail";

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

static bool RunBuild(string project)
{
    using var process = Process.Start(new ProcessStartInfo
    {
        FileName = "dotnet",
        Arguments = $"build \"{project}\" --framework net8.0 --nologo --verbosity quiet",
        RedirectStandardOutput = true,
        RedirectStandardError = true,
        UseShellExecute = false,
    });
    if (process is null) return false;
    process.WaitForExit();
    return process.ExitCode == 0;
}

sealed class AuditResult
{
    public string Status { get; set; } = "fail";
    public string ContractsBuild => ContractsBuildValue ? "pass" : "fail";
    public string LocalizationParity => LocalizationParityValue ? "pass" : "fail";
    public string SourceRoots => SourceRootsValue ? "pass" : "fail";
    [JsonIgnore] public bool ContractsBuildValue { get; set; }
    [JsonIgnore] public bool LocalizationParityValue { get; set; }
    [JsonIgnore] public bool SourceRootsValue { get; set; }
}
