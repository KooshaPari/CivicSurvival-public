#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
project="$repo_root/CivicSurvival.Contracts/CivicSurvival.Contracts.csproj"

if rg -q 'EnvironmentVariableTarget\.User|Mod\.props|Mod\.targets' "$project"; then
  echo "contracts project must not depend on private CS2 toolchain imports" >&2
  exit 1
fi

dotnet build "$project" --framework net8.0 --nologo --verbosity:minimal
