#!/usr/bin/env bash
# Regression test for the FlatBuffers round-trip gate in
# CivicSurvival.PublicAudit. Mutates the committed golden binary
# at .agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin
# and asserts the audit reports flatbuffersRoundTrip=fail.
#
# This proves the gate rejects: bit-flips (in validated bytes), truncation,
# identifier forgery, bogus uoffsets, and undersized buffers. The fixture
# is restored before exit regardless of failure.
set -uo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
project="$repo_root/CivicSurvival.PublicAudit/CivicSurvival.PublicAudit.csproj"
golden="$repo_root/.agileplus/civic-warfare-program/contracts/fixtures/sample-envelope.bin"

if [[ ! -f "$project" || ! -f "$golden" ]]; then
  echo "FAIL: project or golden fixture missing" >&2
  exit 1
fi

backup=$(mktemp)
cp "$golden" "$backup"
trap 'cp "$backup" "$golden"; rm -f "$backup"' EXIT

fail_count=0
pass_count=0

reset() { cp "$backup" "$golden"; }

run_audit() {
  # The audit runner exits 1 when the JSON status is fail; tolerate that here.
  dotnet run --project "$project" -- "$repo_root" --json 2>/dev/null || true
}

mutate_and_assert_fail() {
  local label="$1"
  shift
  reset
  "$@"
  local report
  report=$(run_audit)
  if [[ "$report" == *'"flatbuffersRoundTrip":"fail"'* ]]; then
    echo "PASS: $label caught"
    pass_count=$((pass_count + 1))
  else
    echo "FAIL: $label NOT caught"
    fail_count=$((fail_count + 1))
  fi
  reset
}

# 1. Truncate the binary to half size.
mutate_and_assert_fail "truncation" python3 -c "
with open('$golden','rb') as f: data = f.read()
with open('$golden','wb') as f: f.write(data[:len(data)//2])
"

# 2. Flip a byte that the reader validates: schema_version (uint16) low byte.
#    The test reads schema_version and expects 7; flipping the low byte yields
#    a non-7 value, which the gate should detect.
mutate_and_assert_fail "schema_version bit-flip" python3 -c "
data = bytearray(open('$golden','rb').read())
# schema_version uint16 lives at offset 0x1e..0x20 in the golden
data[0x1e] ^= 0xFF
open('$golden','wb').write(data)
"

# 3. Flip a byte in the payload_type discriminator (index 0 of Envelope).
mutate_and_assert_fail "payload_type bit-flip" python3 -c "
data = bytearray(open('$golden','rb').read())
data[0x14] ^= 0xFF  # payload_type byte (may land elsewhere; gate should still reject malformed union)
open('$golden','wb').write(data)
"

# 4. Forge the file_identifier from CSWP to FAKE.
mutate_and_assert_fail "wrong file_identifier" python3 -c "
data = bytearray(open('$golden','rb').read())
data[4:8] = b'FAKE'
open('$golden','wb').write(data)
"

# 5. Set a uoffset to a huge value (relative offset goes past EOF).
mutate_and_assert_fail "uoffset past EOF" python3 -c "
data = bytearray(open('$golden','rb').read())
data[0:4] = (0xFFFFFFFF).to_bytes(4,'little')
open('$golden','wb').write(data)
"

# 6. Empty file.
mutate_and_assert_fail "empty buffer" sh -c "truncate -s 0 '$golden'"

# 7. Buffer too short (less than 8 bytes — no room for root+identifier).
mutate_and_assert_fail "buffer < 8 bytes" sh -c "truncate -s 4 '$golden'"

# 8. Identical header (CSWP) but zero-length root.
mutate_and_assert_fail "root offset zero" python3 -c "
data = bytearray(open('$golden','rb').read())
data[0:4] = (0).to_bytes(4,'little')
open('$golden','wb').write(data)
"

reset

echo "---"
echo "Roundtrip drift regressions: $pass_count passed, $fail_count failed"
exit $fail_count
