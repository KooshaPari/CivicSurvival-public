# WP01 Go/No-Go Evidence

**Baseline**: `ecc97b3` on `feat/civic-warfare-program`

**Decision date**: 2026-07-29

**Decision owner**: program coordinator
**Decision**: CONDITIONAL NO-GO for production warfare implementation

## Public evidence result

The checked-in public evidence lane is green for the artifacts that exist in
this checkout:

| Gate                     | Result  | Fresh evidence                                                                     |
| ------------------------ | ------- | ---------------------------------------------------------------------------------- |
| Policy/evidence evaluator| pass    | `python3 scripts/civic_quality_gate.py --policy .github/civic-quality-policy.json --strict .` |
| Binding contracts        | pass    | `python3 scripts/contract_check.py`; Node manifest/codegen checks                  |
| UI checks                | pass    | Civic Evidence Gate: declarations, lint rules, UI tests, strict lint, bundle budget |
| Repository tests         | pass    | `python3 -m pytest -q` (18 tests)                                                  |
| Licensed adapter         | pending | Requires legally local Windows/CS2 host                                           |
| AgilePlus evidence       | pending | Supported evidence-recording path unavailable in v0.2.1 CLI                       |

## Blocking conditions

1. The installed-game adapter cannot be compiled or launched from this public macOS clone:
   CS2 managed assemblies, toolkit targets, and private source generators are absent. A licensed
   Windows/CS2 integration host must publish build, launch-smoke, artifact-hash, and provenance evidence.
2. AgilePlus v0.2.1 has no supported CLI/API evidence-recording path. Its v4 database remains
   `planned` with 20 planned WPs; evidence must not be fabricated by direct SQLite mutation.
   The governance surface needs an evidence command or API before `WP01 -> Review -> Done` can be
   represented honestly.
3. `flatc` is unavailable locally. Executable schema conformance is deferred to WP02 with a pinned
   compiler/runtime toolchain.

## Release interpretation

The public repository is now source-auditable and CI-gated. It is not an independently reproducible
installed-game release. No production warfare behavior may merge until the licensed adapter evidence,
AgilePlus evidence recording, and WP01 review approval exist.

## Next lane: WP02-A

Before combat or economy behavior, implement the native boundary: pinned Cargo workspace, FlatBuffers
roots and generated bindings, stable FFI errors/status serialization, panic containment, bounded buffers,
transactional save-load semantics, and golden vectors for empty batches, duplicate commands, invalid
handles, ABI mismatch, and insufficient output buffers.

The preserved warfare-program archive contains a historical WP02-A workspace
prototype under `native/`, but the current public checkout intentionally does
not contain that tree. It must be reintroduced only through a focused successor
PR after WP01 evidence is accepted; archive contents are provenance, not current
implementation evidence. No claim is made here about a present Rust workspace,
FlatBuffers verification, C ABI lifecycle, or gameplay behavior.
