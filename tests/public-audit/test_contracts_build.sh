#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
project="$repo_root/CivicSurvival.Contracts/CivicSurvival.Contracts.csproj"

if grep -Eq 'EnvironmentVariableTarget\.User|Mod\.props|Mod\.targets' "$project"; then
  echo "contracts project must not depend on private CS2 toolchain imports" >&2
  exit 1
fi

if ! grep -Eq '<TargetFrameworks>net8\.0;net48</TargetFrameworks>' "$project"; then
  echo "contracts project must target net8.0 and net48 for mod/tool compatibility" >&2
  exit 1
fi

if grep -q 'Math\.Clamp' "$repo_root/CivicSurvival.Contracts" --include='*.cs'; then
  echo "generated contracts must use ContractMath.Clamp for net48 compatibility" >&2
  exit 1
fi

dotnet build "$project" --framework net8.0 --nologo --verbosity:minimal
dotnet build "$project" --framework net48 --nologo --verbosity:minimal
