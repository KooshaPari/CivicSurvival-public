#!/usr/bin/env bash
# Regression test for the WP02-A FlatBuffers schema contract gate.
# This test proves the public-audit runner correctly detects drift in
# the .agileplus/civic-warfare-program/contracts/ files. The runner
# should fail-fast on:
#   - missing required enum members (shrinking the wire contract),
#   - removed root_type or file_identifier (silent wire-format change),
#   - removal of any csw_* ABI function from the C header,
#   - introduction of proprietary game SDK symbols in the public header.
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
project="$repo_root/CivicSurvival.PublicAudit/CivicSurvival.PublicAudit.csproj"

if [[ ! -f "$project" ]]; then
  echo "public audit runner project is missing" >&2
  exit 1
fi

fbs="$repo_root/.agileplus/civic-warfare-program/contracts/warfare.fbs"
header="$repo_root/.agileplus/civic-warfare-program/contracts/civic_warfare.h"
if [[ ! -f "$fbs" || ! -f "$header" ]]; then
  echo "required contract files missing" >&2
  exit 1
fi

backup_dir=$(mktemp -d)
trap 'rm -rf "$backup_dir"' EXIT
cp "$fbs" "$backup_dir/warfare.fbs"
cp "$header" "$backup_dir/civic_warfare.h"

restore() {
  cp "$backup_dir/warfare.fbs" "$fbs"
  cp "$backup_dir/civic_warfare.h" "$header"
}
check_fails_with() {
  local label="$1"
  shift
  # Build backup of current (original) files FIRST, then mutate.
  # NOTE: backup is already in $backup_dir from script startup.
  # Mutate contract.
  "$@"
  if report=$(dotnet run --project "$project" -- "$repo_root" --json 2>/dev/null || true) && \
     [[ "$report" == *'"flatbuffersSchema":"fail"'* ]]; then
    echo "PASS: detected $label"
  else
    echo "FAIL: did not detect $label; got: $report" >&2
    restore
    exit 1
  fi
  restore
}

# Build once so the rest of the test runs quickly.
dotnet build "$project" --nologo --verbosity:quiet >/dev/null 2>&1

# Drift 1: shrink CommandKind by removing a member.
check_fails_with "removed CommandKind member" bash -c "
  sed -i.bak '/^  SetMission,\$/d' '$fbs'
  rm -f '$fbs.bak'
"

# Drift 2: shrink DecisionCode by removing a member.
check_fails_with "removed DecisionCode member" bash -c "
  sed -i.bak '/^  InsufficientResources,\$/d' '$fbs'
  rm -f '$fbs.bak'
"

# Drift 3: change file_identifier (wire format change).
check_fails_with "changed file_identifier" bash -c "
  sed -i.bak 's/CSWP/CSWQ/' '$fbs'
  rm -f '$fbs.bak'
"

# Drift 4: remove csw_status_into from the public ABI.
check_fails_with "removed csw_status_into" bash -c "
  sed -i.bak '/csw_status_into/d' '$header'
  rm -f '$header.bak'
"

# Drift 5: introduce a proprietary game SDK reference in the public header.
check_fails_with "ColossalOrder reference" bash -c "
  printf '\n/* leak */\n#include <ColossalOrder/CitiesSkylinesApi.h>\n' >> '$header'
"

# Sanity: restoring original files lets the gate pass again.
report=$(dotnet run --project "$project" -- "$repo_root" --json 2>/dev/null)
if [[ "$report" == *'"flatbuffersSchema":"pass"'* ]]; then
  echo "PASS: schema gate returns to pass after restore"
else
  echo "FAIL: schema gate still failing after restore: $report" >&2
  exit 1
fi

echo "All FlatBuffers contract drift regressions are detected."
