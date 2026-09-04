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

# Run the cross-language drift test (Python reader, dependency-free)
cross_lang_output=$(python3 "$repo_root/tests/run_cross_lang_drift.py" 2>&1 || true)
echo "$cross_lang_output"
if [[ "$cross_lang_output" != *"9/9 cross-lang drift cases passed"* ]]; then
  echo "FAIL: cross-language drift test did not pass" >&2
  exit 1
fi

# WP02-C: ProjectionDelta cross-language drift (dependency-free Python runner)
wp02c_output=$(python3 "$repo_root/tests/run_wp02c_drift.py" 2>&1 || true)
echo "$wp02c_output"
if [[ "$wp02c_output" != *"8/8 wp02c drift cases passed"* ]]; then
  echo "FAIL: wp02c drift test did not pass" >&2
  exit 1
fi

# WP02-D: SaveEnvelope cross-language drift (dependency-free Python runner)
wp02d_output=$(python3 "$repo_root/tests/run_wp02d_drift.py" 2>&1 || true)
echo "$wp02d_output"
if [[ "$wp02d_output" != *"8/8 wp02d drift cases passed"* ]]; then
  echo "FAIL: wp02d drift test did not pass" >&2
  exit 1
fi

# WP02-S: Cross-language stress fuzzing (50 fixtures per union arm, 150 total)
# The stress runner exits 0 in two valid audit states:
#   (a) flatc in PATH:  emits "150/150 wp02s stress cases pass (cross-language)"
#   (b) flatc missing:  emits "SKIPPED: flatc not in PATH; ..." then exits 0
# Flatc is not shipped in the CI image, so (b) is the normal CI outcome. Both
# states are valid; the gate only fails if NEITHER substring matches.
wp02s_output=$(python3 "$repo_root/tests/run_wp02s_stress.py" 2>&1 || true)
echo "$wp02s_output"
if [[ "$wp02s_output" != *"150/150 wp02s stress cases pass"* ]] && [[ "$wp02s_output" != *"SKIPPED: flatc not in PATH"* ]]; then
  echo "FAIL: wp02s stress test did not pass" >&2
  exit 1
fi
