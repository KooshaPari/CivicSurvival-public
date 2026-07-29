#!/usr/bin/env bash
set -euo pipefail

# Generate the pinned Rust bindings and exercise the runtime verifier against
# both a valid Envelope and hostile input.  This is intentionally a no-op when
# flatc is not installed locally; CI installs the exact pinned compiler first.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
schema="$repo_root/.agileplus/civic-warfare-program/contracts/warfare.fbs"
toolchain="$repo_root/native/flatbuffers-toolchain.toml"
expected="$(sed -n 's/^release = "\([^"]*\)"/\1/p' "$toolchain")"

if ! command -v flatc >/dev/null 2>&1; then
  echo "flatc unavailable; verifier harness deferred (expected $expected)"
  exit 0
fi
version="$(flatc --version | sed -n 's/.*version \([0-9][0-9.]*\).*/\1/p')"
[[ "$version" == "$expected" ]] || { echo "flatc $version != $expected" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/src"
flatc --rust -o "$tmp/src" "$schema"

cat >"$tmp/Cargo.toml" <<'EOF'
[package]
name = "civic-flatbuffer-verifier"
version = "0.0.0"
edition = "2021"
[dependencies]
flatbuffers = "25.12.19"
EOF
cat >"$tmp/src/main.rs" <<'EOF'
mod warfare_generated;
use flatbuffers::FlatBufferBuilder;
use warfare_generated::civic_survival::warfare::contracts::{
    Envelope, EnvelopeArgs, RootPayload,
};

fn valid() -> Vec<u8> {
    let mut b = FlatBufferBuilder::new();
    let envelope = Envelope::create(&mut b, &EnvelopeArgs {
        payload_type: RootPayload::NONE,
        payload: None,
    });
    b.finish(envelope, Some(b"CSWP"));
    b.finished_data().to_vec()
}

fn main() {
    let good = valid();
    assert!(flatbuffers::root::<Envelope>(&good).is_ok(), "valid Envelope rejected");

    let mut truncated = good.clone();
    truncated.truncate(truncated.len() - 1);
    assert!(flatbuffers::root::<Envelope>(&truncated).is_err(), "truncated buffer accepted");

    let mut bad_identifier = good;
    bad_identifier[4..8].copy_from_slice(b"NOPE");
    assert!(flatbuffers::root::<Envelope>(&bad_identifier).is_err(), "bad identifier accepted");
}
EOF
(cd "$tmp" && cargo run --quiet --locked)
echo "flatc $version generated Rust verifier vectors passed"
