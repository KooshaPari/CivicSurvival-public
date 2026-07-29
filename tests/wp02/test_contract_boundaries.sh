#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
header="$repo_root/.agileplus/civic-warfare-program/contracts/civic_warfare.h"
schema="$repo_root/.agileplus/civic-warfare-program/contracts/warfare.fbs"
api="$repo_root/.agileplus/civic-warfare-program/contracts/public-api.md"

command -v clang >/dev/null
clang -fsyntax-only -x c "$header"

if grep -q 'typedef struct CswStatus' "$header"; then
  echo "platform-dependent C status struct crosses ABI" >&2
  exit 1
fi
grep -q 'csw_status_into' "$header"
grep -q 'union RootPayload' "$schema"
grep -q 'root_type Envelope' "$schema"
grep -q 'payload:RootPayload (id: 1)' "$schema"
grep -q 'removals:\[ubyte\]' "$schema"
grep -q 'alerts:\[ubyte\]' "$schema"
grep -q 'explanations:\[ubyte\]' "$schema"
grep -q 'csw_status_into' "$api"

echo "WP02 contract boundary checks passed"
