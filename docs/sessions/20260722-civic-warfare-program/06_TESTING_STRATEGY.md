# Testing Strategy Index

The current public checkout does not contain the historical `tests/public-audit/`,
`CivicSurvival.PublicAudit/`, `tests/wp02/`, or `native/` trees referenced by
earlier design notes. Those paths are preserved only in the archived warfare
branch and are not executable evidence for this checkout.

The current public evidence lane is the checked-in `Civic Evidence Gate` in
`.github/workflows/ci.yml`. It runs the versioned Python policy evaluator,
binding-contract checks, UI declaration/lint-rule/behavioral tests, strict
lint, and bundle-budget checks. Local equivalents are:

```bash
python3 -m pytest -q
python3 scripts/contract_check.py
node Tools/generate-binding-manifest.js --check
node Tools/sync-binding-codegen.js --check
python3 scripts/civic_quality_gate.py --policy .github/civic-quality-policy.json --strict .
```

The installed-game adapter remains intentionally excluded: it requires legally
local CS2 assemblies, the modding toolkit, and omitted private generators. A
licensed Windows/CS2 host must provide separate build, launch-smoke,
artifact-hash, and provenance evidence before WP01 can pass.

The required host bundle is represented by
`.agileplus/civic-warfare-program/wp01-evidence.template.json` and checked with
`python3 scripts/verify_wp01_evidence.py REPO MANIFEST`. The verifier fails
closed on missing records, wrong subject commits, invalid paths, or hash
mismatches; the checked-in template remains pending by design.

WP02-A is a planned successor PR, not current implementation evidence. It must
reintroduce a pinned Rust workspace, FlatBuffers compiler/runtime lockstep,
safe opaque-handle FFI, verifier coverage, and C smoke tests through fresh
test-first commits after the WP01 gate is accepted.
