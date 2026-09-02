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
[[ "$report" == *'"flatbuffersSchema":"pass"'* ]]
[[ "$report" == *'"flatbuffersRoundTrip":"pass"'* ]]
[[ "$report" == *'"flatbuffersCrossLang":"pass"'* ]]

# Run the cross-language drift test (Python reader)
if [[ -f "$repo_root/tests/test_cross_lang_drift.py" ]]; then
  cross_lang_output=$(python3 -m pytest "$repo_root/tests/test_cross_lang_drift.py" -q 2>&1 || true)
  if [[ "$cross_lang_output" != *"9 passed"* ]]; then
    echo "FAIL: cross-language drift test did not pass" >&2
    echo "$cross_lang_output" >&2
    exit 1
  fi
fi
