#!/usr/bin/env bash
# Regenerate the WP02-C ProjectionDelta golden fixture.
#
# The fixture is hand-crafted to exercise the second RootPayload union
# member (ProjectionDelta) with the full field set:
#   - 2 CommandDecision entries (Accepted + InsufficientResources)
#   - 1 CommandOutcome entry (with all 6 fields populated)
#   - non-empty views, removals, explanations byte-vectors
#   - empty alerts (default-state vector)
#   - state_hash, base_revision, new_revision, tick all populated
#
# Output:
#   sample-projection.bin (replaces existing fixture if any)
#
# Cross-validation: flatc --json --raw-binary --strict-json emits the
# canonical JSON; tests/flatbuffers_reader.py produces equivalent
# Python-decoded JSON. Both must agree for the WP02-C cross-language
# gate to pass.

set -euo pipefail

# Resolve repo root: this script is at
# .agileplus/civic-warfare-program/contracts/fixtures/generate-projection-fixture.sh
# -> 4 levels up is the repo root.
repo_root="$(cd "$(dirname "$0")/../../../.." && pwd)"

schema="$repo_root/.agileplus/civic-warfare-program/contracts/warfare.fbs"
fixture_dir="$repo_root/.agileplus/civic-warfare-program/contracts/fixtures"
fixture="$fixture_dir/sample-projection.bin"

# Build the JSON input in a temp file (flatc needs a real file with the schema-aligned name).
json_input="$(mktemp -t wp02c-projection.XXXXXX.json)"

cat > "$json_input" <<'JSON'
{
  "payload_type": "ProjectionDelta",
  "payload": {
    "campaign_id": [1,2,3],
    "observer_id": [7],
    "base_revision": 100,
    "new_revision": 101,
    "tick": 500,
    "state_hash": [170,187,204,221],
    "decisions": [
      {
        "command_id": [1,2,3,4],
        "code": "Accepted",
        "reason_key": "ok",
        "validated_revision": 100,
        "details": [1]
      },
      {
        "command_id": [5,6,7],
        "code": "InsufficientResources",
        "reason_key": "low_fuel",
        "validated_revision": 99,
        "details": []
      }
    ],
    "outcomes": [
      {
        "command_id": [1,2,3,4],
        "tick": 500,
        "sequence": 1,
        "context": 2,
        "kind": 5,
        "payload": [255,0]
      }
    ],
    "views": [16,32,48],
    "removals": [64],
    "alerts": [],
    "explanations": [85,102]
  }
}
JSON

# flatc derives the output filename by appending .bin to the JSON input filename.
# Move the generated file to the canonical location.
out_dir="$(mktemp -d)"
flatc --binary --strict-json --force-defaults -o "$out_dir" "$schema" "$json_input"

# Find the generated .bin (flatc appends .bin to the JSON basename).
generated="$(find "$out_dir" -name '*.bin' | head -1)"
if [[ -z "$generated" ]]; then
  echo "ERROR: flatc produced no .bin output" >&2
  exit 1
fi

cp "$generated" "$fixture"

# Round-trip verification: decode and re-emit.
verify_dir="$(mktemp -d)"
flatc --json --raw-binary --strict-json -o "$verify_dir" "$schema" -- "$fixture"
echo "WP02-C fixture regenerated: $fixture ($(wc -c < "$fixture") bytes)"
echo "Round-trip verified: $(ls "$verify_dir"/sample-projection.json 2>/dev/null || echo "$verify_dir"/*.json)"

# Clean up temp dirs/files
rm -rf "$out_dir" "$verify_dir" "$json_input"

# Remove stale debug files in fixtures dir.
find "$fixture_dir" -name 'wp02c-projection.*.bin' -not -name 'sample-projection.bin' -delete 2>/dev/null || true
find "$fixture_dir" -name 'wp02c-projection.*.json' -not -name 'sample-projection.json' -delete 2>/dev/null || true
rm -rf "$fixture_dir/.wp02c-baseline"
