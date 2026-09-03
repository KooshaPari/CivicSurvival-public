#!/usr/bin/env bash
# Smoke test: invoke the 3 C# cross-language gates (WP02-B/C/D) against
# the 3 committed golden fixtures, without touching Program.cs.
set -euo pipefail
repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"

dotnet build CivicSurvival.PublicAudit/CivicSurvival.PublicAudit.csproj --nologo --verbosity:quiet 2>&1 | tail -2

dll=$(find CivicSurvival.PublicAudit/bin -name 'CivicSurvival.PublicAudit.dll' -path '*net8.0*' | head -1)
test -n "$dll" || { echo "FATAL: built DLL not found"; exit 2; }

tmp=$(mktemp -d)
cat > "$tmp/Runner.csproj" << PROJ
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <RollForward>LatestMajor</RollForward>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="CivicSurvival.PublicAudit">
      <HintPath>${repo_root}/${dll}</HintPath>
    </Reference>
  </ItemGroup>
</Project>
PROJ

cat > "$tmp/Program.cs" << 'PROG'
using CivicSurvival.PublicAudit;

string repo = Environment.CurrentDirectory;
int failed = 0;
string? e;

if (FlatbuffersCrossLangCheck.CheckFlatbuffersCrossLang(repo, out e)) {
    Console.WriteLine("PASS: WP02-B:FlatbuffersCrossLang (sample-envelope)");
} else {
    Console.WriteLine($"FAIL: WP02-B:FlatbuffersCrossLang -- {e}");
    failed++;
}

if (FlatbuffersProjectionCheck.CheckFlatbuffersProjection(repo, out e)) {
    Console.WriteLine("PASS: WP02-C:FlatbuffersProjection (sample-projection)");
} else {
    Console.WriteLine($"FAIL: WP02-C:FlatbuffersProjection -- {e}");
    failed++;
}

if (FlatbuffersSaveCheck.CheckFlatbuffersSave(repo, out e)) {
    Console.WriteLine("PASS: WP02-D:FlatbuffersSave (sample-save)");
} else {
    Console.WriteLine($"FAIL: WP02-D:FlatbuffersSave -- {e}");
    failed++;
}

Console.WriteLine(failed == 0 ? "OK: all 3 cross-language gates PASS" : $"FAIL: {failed} gate(s) FAILED");
Environment.Exit(failed == 0 ? 0 : 1);
PROG

dotnet run --project "$tmp/Runner.csproj" 2>&1 | tail -15
ec=$?
rm -rf "$tmp"
exit $ec
