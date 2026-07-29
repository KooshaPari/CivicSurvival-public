#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
metadata=$(cargo metadata --manifest-path "$repo_root/native/Cargo.toml" --no-deps --format-version 1)
for package in civic-model civic-rules civic-application civic-ffi civic-headless; do
  grep -q "\"name\":\"$package\"" <<<"$metadata"
done

[[ "$(grep -c '^name = ' "$repo_root/native/Cargo.toml")" -eq 0 ]]
grep -q 'members = \["model", "rules", "application", "ffi", "headless"\]' "$repo_root/native/Cargo.toml"
cargo test --manifest-path "$repo_root/native/Cargo.toml" --workspace --locked
cargo build --manifest-path "$repo_root/native/Cargo.toml" --package civic-ffi --locked
