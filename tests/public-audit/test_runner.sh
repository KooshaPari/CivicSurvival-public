#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
project="$repo_root/CivicSurvival.PublicAudit/CivicSurvival.PublicAudit.csproj"

if [[ ! -f "$project" ]]; then
  echo "public audit runner project is missing" >&2
  exit 1
fi

report=$(dotnet run --project "$project" -- "$repo_root" --json)
printf '%s\n' "$report"
[[ "$report" == *'"status":"pass"'* ]]
[[ "$report" == *'"contractsBuild":"pass"'* ]]
[[ "$report" == *'"localizationParity":"pass"'* ]]
[[ "$report" == *'"sourceRoots":"pass"'* ]]
