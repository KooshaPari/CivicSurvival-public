// CivicSurvival Mod Installer - .NET 9 Console App
// Compile: dotnet publish -c Release -r win-x64 --self-contained false
//
// Usage:
//   civicsurvival-installer install    <mod-dll-or-built-publishdir> [--game-path <path>]
//   civicsurvival-installer update     <new-mod-dll-or-built-publishdir> [--game-path <path>]
//   civicsurvival-installer remove     [--game-path <path>]
//   civicsurvival-installer status     [--game-path <path>]
//   civicsurvival-installer launch     [--game-path <path>] [--skyve|--bepinex|--steam]
//
// Cross-platform: works on Windows, Linux, macOS (auto-discovers install paths)

using System.Diagnostics;
using System.Net.Http;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace CivicSurvivalInstaller;

public static class Program
{
    private const string ModName = "CivicSurvival";
    private const string PluginFolderName = "CivicSurvival";
    private const string InstallStampFile = ".civicsurvival-installed";
    private const string LatestReleaseApi = "https://api.github.com/repos/KooshaPari/CivicSurvival-public/releases/latest";
    // BepInEx layout on Windows: <Game>/BepInEx/plugins/<PluginFolder>/<dll>
    // With monomod (built-in), BepInEx loads everything in plugins/. We still
    // sandbox into our own subfolder so install/remove stays atomic and idempotent.

    public static async Task<int> Main(string[] args)
    {
        try
        {
            if (args.Length == 0)
            {
                PrintUsage();
                return 64; // EX_USAGE
            }

            var gamePath = ResolveGamePath(GetOption(args, "--game-path"));
            var command = args[0].ToLowerInvariant();
            var positional = args.Skip(1).Where(a => !a.StartsWith("--")).ToArray();

            int code;
            switch (command)
            {
                case "install":
                    code = await InstallAsync(positional, gamePath);
                    break;
                case "update":
                    code = await UpdateAsync(positional, gamePath);
                    break;
                case "remove":
                case "uninstall":
                    code = await RemoveAsync(gamePath);
                    break;
                case "status":
                    code = await Task.FromResult(Status(gamePath));
                    break;
                case "launch":
                    code = await LaunchAsync(gamePath, args);
                    break;
                case "version":
                case "--version":
                case "-v":
                    code = Version();
                    break;
                case "help":
                case "--help":
                case "-h":
                    code = Help();
                    break;
                default:
                    code = Unknown(command);
                    break;
            }
            return code;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"error: {ex.Message}");
            return 1;
        }
    }

    // ---------------------------------------------------------------------
    // Subcommands
    // ---------------------------------------------------------------------

    private static async Task<int> InstallAsync(string[] positional, string gamePath)
    {
        if (positional.Length == 0)
        {
            Console.Error.WriteLine("install: missing source (path to .dll or built publish dir)");
            return 64;
        }
        var source = positional[0];
        var modDll = ResolveModDll(source);

        var pluginsRoot = PluginsRoot(gamePath);
        EnsureDirectory(pluginsRoot);
        var pluginDir = Path.Combine(pluginsRoot, PluginFolderName);
        EnsureDirectory(pluginDir);

        var targetDll = Path.Combine(pluginDir, $"{ModName}.dll");
        var modsJson = Path.Combine(pluginDir, $"{ModName}.json");

        File.Copy(modDll, targetDll, overwrite: true);
        await WriteManifest(pluginDir, modDll, isUpdate: false);

        StampInstalled(pluginDir);
        Console.WriteLine($"installed: {targetDll}");
        Console.WriteLine($"manifest : {modsJson}");
        return 0;
    }

    private static async Task<int> UpdateAsync(string[] positional, string gamePath)
    {
        if (positional.Length == 0)
        {
            Console.Error.WriteLine("update: missing source (path to new .dll or built publish dir)");
            return 64;
        }
        var pluginDir = Path.Combine(PluginsRoot(gamePath), PluginFolderName);
        if (!IsInstalled(pluginDir))
        {
            Console.Error.WriteLine("update: mod not installed; run install first");
            return 1;
        }
        var modDll = ResolveModDll(positional[0]);
        var targetDll = Path.Combine(pluginDir, $"{ModName}.dll");
        File.Copy(modDll, targetDll, overwrite: true);
        await WriteManifest(pluginDir, modDll, isUpdate: true);
        Console.WriteLine($"updated: {targetDll}");
        return 0;
    }

    private static async Task<int> RemoveAsync(string gamePath)
    {
        var pluginDir = Path.Combine(PluginsRoot(gamePath), PluginFolderName);
        if (!Directory.Exists(pluginDir))
        {
            Console.WriteLine("not installed.");
            return 0;
        }
        Directory.Delete(pluginDir, recursive: true);
        Console.WriteLine($"removed: {pluginDir}");
        return 0;
    }

    private static int Status(string gamePath)
    {
        var pluginDir = Path.Combine(PluginsRoot(gamePath), PluginFolderName);
        if (!Directory.Exists(pluginDir))
        {
            Console.WriteLine("not installed.");
            return 0;
        }
        var stamp = TryReadStamp(pluginDir);
        var modsJson = Path.Combine(pluginDir, $"{ModName}.json");
        Console.WriteLine($"installed: yes  ({pluginDir})");
        if (File.Exists(modsJson))
        {
            var json = JsonSerializer.Deserialize<Manifest>(File.ReadAllText(modsJson));
            if (json is not null)
            {
                Console.WriteLine($"source-dll: {json.SourceDll}");
                Console.WriteLine($"version   : {json.InstalledVersion}");
                Console.WriteLine($"installed : {json.InstalledAtUtc:u}");
                Console.WriteLine($"updated   : {json.LastUpdatedAtUtc:u}");
            }
        }
        if (stamp is not null) Console.WriteLine($"stamp     : {stamp}");
        return 0;
    }

    private static async Task<int> LaunchAsync(string gamePath, string[] args)
    {
        var exe = Path.Combine(gamePath, RuntimeInformation.IsOSPlatform(OSPlatform.Windows)
            ? "Cities2.exe"
            : "Cities2.x86_64");
        if (!File.Exists(exe))
        {
            Console.Error.WriteLine($"launch: game executable not found at {exe}");
            return 1;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = exe,
            WorkingDirectory = gamePath,
            UseShellExecute = true,
        };
        Console.WriteLine($"launching: {exe}");
        Process.Start(startInfo);
        return 0;
    }

    private static int Version()
    {
        var v = typeof(Program).Assembly.GetName().Version?.ToString() ?? "0.0.0";
        Console.WriteLine($"civicsurvival-installer {v}");
        return 0;
    }

    private static int Help()
    {
        PrintUsage();
        return 0;
    }

    private static int Unknown(string cmd)
    {
        Console.Error.WriteLine($"unknown command: {cmd}");
        PrintUsage();
        return 64;
    }

    // ---------------------------------------------------------------------
    // Path resolution
    // ---------------------------------------------------------------------

    private static string ResolveGamePath(string? overridePath)
    {
        if (!string.IsNullOrEmpty(overridePath) && Directory.Exists(overridePath))
            return overridePath!;

        var envGame = Environment.GetEnvironmentVariable("CITIES_SKYLINES_II_PATH");
        if (!string.IsNullOrEmpty(envGame) && Directory.Exists(envGame))
            return envGame;

        // Windows defaults
        var candidates = new List<string>();
        if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
        {
            var steamRoots = new[]
            {
                @"C:\Program Files (x86)\Steam\steamapps\common\Cities Skylines II",
                @"C:\SteamLibrary\steamapps\common\Cities Skylines II",
                @"D:\SteamLibrary\steamapps\common\Cities Skylines II",
                @"G:\SteamLibrary\steamapps\common\Cities Skylines II",
            };
            candidates.AddRange(steamRoots);
        }
        else if (RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
        {
            var home = Environment.GetEnvironmentVariable("HOME") ?? "/root";
            candidates.Add(Path.Combine(home, ".steam", "steam", "steamapps", "common", "Cities Skylines II"));
            candidates.Add(Path.Combine(home, ".local", "share", "Steam", "steamapps", "common", "Cities Skylines II"));
        }
        else if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX))
        {
            var home = Environment.GetEnvironmentVariable("HOME") ?? "/Users";
            candidates.Add(Path.Combine(home, "Library", "Application Support", "Steam", "steamapps", "common", "Cities Skylines II"));
        }

        foreach (var c in candidates.Distinct())
            if (Directory.Exists(c)) return c;

        throw new InvalidOperationException(
            "could not locate Cities: Skylines II install path. Set CITIES_SKYLINES_II_PATH or pass --game-path");
    }

    private static string PluginsRoot(string gamePath)
        => Path.Combine(gamePath, "BepInEx", "plugins");

    private static string ResolveModDll(string source)
    {
        if (File.Exists(source) && source.EndsWith(".dll", StringComparison.OrdinalIgnoreCase))
            return source;
        if (Directory.Exists(source))
        {
            // pick first *.dll that doesn't look like a ref assembly
            var dll = Directory.EnumerateFiles(source, "*.dll", SearchOption.AllDirectories)
                .FirstOrDefault(p =>
                {
                    var n = Path.GetFileName(p);
                    if (n.StartsWith("ref_", StringComparison.OrdinalIgnoreCase)) return false;
                    if (n.StartsWith("System.", StringComparison.OrdinalIgnoreCase)) return false;
                    if (n.StartsWith("Unity.", StringComparison.OrdinalIgnoreCase) && !n.Equals("UnityEngine.dll", StringComparison.OrdinalIgnoreCase) && !n.Equals("UnityEngine.CoreModule.dll", StringComparison.OrdinalIgnoreCase)) return false;
                    return true;
                });
            if (dll is not null) return dll;
            throw new InvalidOperationException($"no suitable .dll found in {source}");
        }
        throw new InvalidOperationException($"source not found: {source}");
    }

    // ---------------------------------------------------------------------
    // Manifest + stamp
    // ---------------------------------------------------------------------

    private record Manifest
    {
        [JsonPropertyName("id")]            public string Id { get; set; } = ModName.ToLowerInvariant();
        [JsonPropertyName("name")]          public string Name { get; set; } = ModName;
        [JsonPropertyName("source_dll")]    public string SourceDll { get; set; } = "";
        [JsonPropertyName("installed_version")]  public string InstalledVersion { get; set; } = "";
        [JsonPropertyName("installed_at_utc")]   public DateTime InstalledAtUtc { get; set; }
        [JsonPropertyName("last_updated_at_utc")] public DateTime LastUpdatedAtUtc { get; set; }
        [JsonPropertyName("installer")]     public string Installer { get; set; } = "civicsurvival-installer";
    }

    private static async Task WriteManifest(string pluginDir, string modDll, bool isUpdate)
    {
        var modsJson = Path.Combine(pluginDir, $"{ModName}.json");
        Manifest m;
        if (File.Exists(modsJson))
        {
            m = JsonSerializer.Deserialize<Manifest>(await File.ReadAllTextAsync(modsJson)) ?? new Manifest();
        }
        else
        {
            m = new Manifest
            {
                InstalledAtUtc = DateTime.UtcNow,
            };
        }
        m.SourceDll       = Path.GetFileName(modDll);
        m.InstalledVersion = typeof(Program).Assembly.GetName().Version?.ToString() ?? "0.0.0";
        m.LastUpdatedAtUtc = DateTime.UtcNow;

        await File.WriteAllTextAsync(modsJson, JsonSerializer.Serialize(m, new JsonSerializerOptions { WriteIndented = true }));
    }

    private static void StampInstalled(string pluginDir)
    {
        File.WriteAllText(Path.Combine(pluginDir, InstallStampFile),
            $"{ModName} installed at {DateTime.UtcNow:o}");
    }

    private static bool IsInstalled(string pluginDir)
        => Directory.Exists(pluginDir)
        && File.Exists(Path.Combine(pluginDir, InstallStampFile));

    private static string? TryReadStamp(string pluginDir)
    {
        var p = Path.Combine(pluginDir, InstallStampFile);
        return File.Exists(p) ? File.ReadAllText(p).Trim() : null;
    }

    // ---------------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------------

    private static string? GetOption(string[] args, string name)
    {
        for (int i = 0; i < args.Length - 1; i++)
            if (args[i] == name) return args[i + 1];
        return null;
    }

    private static void EnsureDirectory(string p)
    {
        if (!Directory.Exists(p)) Directory.CreateDirectory(p);
    }

    private static void PrintUsage()
    {
        Console.WriteLine("CivicSurvival Mod Installer (compiled .NET 9 exe).");
        Console.WriteLine();
        Console.WriteLine("Usage:");
        Console.WriteLine("  civicsurvival-installer install    <dll-or-publishdir> [--game-path <path>]");
        Console.WriteLine("  civicsurvival-installer update     <dll-or-publishdir> [--game-path <path>]");
        Console.WriteLine("  civicsurvival-installer remove     [--game-path <path>]");
        Console.WriteLine("  civicsurvival-installer status     [--game-path <path>]");
        Console.WriteLine("  civicsurvival-installer launch     [--game-path <path>]");
        Console.WriteLine("  civicsurvival-installer version");
        Console.WriteLine();
        Console.WriteLine("Env: CITIES_SKYLINES_II_PATH can override auto-discovery.");
        Console.WriteLine("Auto-discovery: Steam install paths on Windows/Linux/macOS.");
    }
}
