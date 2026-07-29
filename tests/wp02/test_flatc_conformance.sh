#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
schema="$repo_root/.agileplus/civic-warfare-program/contracts/warfare.fbs"
toolchain="$repo_root/native/flatbuffers-toolchain.toml"

expected_release="$(sed -n 's/^release = "\([^"]*\)"/\1/p' "$toolchain")"
if ! command -v flatc >/dev/null 2>&1; then
  echo "flatc unavailable; expected pinned release $expected_release (conformance deferred)"
  exit 0
fi

version="$(flatc --version | sed -n 's/.*version \([0-9][0-9.]*\).*/\1/p')"
if [[ "$version" != "$expected_release" ]]; then
  echo "flatc $version does not match pinned release $expected_release" >&2
  exit 1
fi

out_dir="$(mktemp -d)"
trap 'rm -rf "$out_dir"' EXIT
flatc --strict-json --cpp --rust --ts --python -o "$out_dir" "$schema"
test -s "$out_dir/warfare_generated.h"
test -s "$out_dir/warfare_generated.rs"
test -s "$out_dir/warfare_generated.ts"
test -s "$out_dir/warfare_generated.py"
echo "flatc $version schema generation passed"
