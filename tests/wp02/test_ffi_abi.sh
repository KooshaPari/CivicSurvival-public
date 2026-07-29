#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
header_dir="$repo_root/.agileplus/civic-warfare-program/contracts"
target_dir="$repo_root/native/target/debug"

command -v clang >/dev/null
cargo build --manifest-path "$repo_root/native/Cargo.toml" --package civic-ffi --locked

if [[ -f "$target_dir/libcivic_ffi.dylib" ]]; then
  library="$target_dir/libcivic_ffi.dylib"
elif [[ -f "$target_dir/libcivic_ffi.so" ]]; then
  library="$target_dir/libcivic_ffi.so"
else
  echo "civic-ffi cdylib was not produced" >&2
  exit 1
fi

out_dir="$(mktemp -d)"
trap 'rm -rf "$out_dir"' EXIT
clang -std=c11 -Wall -Wextra -Werror \
  -I "$header_dir" "$repo_root/tests/wp02/ffi_smoke.c" "$library" \
  -Wl,-rpath,"$target_dir" -o "$out_dir/ffi-smoke"
"$out_dir/ffi-smoke"
echo "C-to-Rust FFI ABI smoke passed"
