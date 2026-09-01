# Release notes — v0.3.25

**Release date:** 2026-08-31
**Type:** Patch (test infrastructure + dep-delta gate fix)
**Risk:** Low — no gameplay changes, no public-facing changes.

## Summary

v0.3.25 ships two infrastructure improvements that tighten the public-source
mirror's correctness story without changing anything player-facing.

## What's new

### Localization regression suite

A new pytest suite at `tests/test_localization_keys.py` locks in the
3-locale key parity:

- All 3 locales (`en-US`, `uk-UA`, `zh-CN`) contain exactly **3,531 keys**.
- Cross-locale key-set parity is **perfect** — zero drift in either direction.
- Identical values across all 3 locales are confined to exactly **13 keys**,
  all of which are legitimate (proper nouns, raw numbers, format templates).
- The test uses a **bidirectional equality check** against an auto-discovered
  ground truth, so both new drift and allowlist rot fail loudly.
- A second sanity test guards against accidentally adding translatable
  sentences to the allowlist.

This is a CI-eligible regression guard: future locale changes that introduce
key drift will fail `uv run pytest` before merge.

### Dependency-delta gate fix

The dependency-delta CI scanner previously failed on every `.csproj` change
in this public mirror, even when the change was a purely cosmetic
metadata edit (`<Version>`, `<AssemblyName>`, `<Description>`). The fix:

- Adds `_METADATA_ONLY_CSPROJ_ELEMENTS` — a frozen set of 15 MSBuild
  elements whose change does NOT alter the resolved package graph.
- Adds `_is_metadata_only_csproj_diff()` — parses the unified-diff
  `+/-` lines and confirms every touched tag is on the allowlist.
- `build_scan_plan` now accepts an optional `diff_provider`; `main()`
  wires it to a per-file `git diff` via the new `_file_diff` helper.
- Changes that touch `<PackageReference>`, `<Reference>`,
  `<ProjectReference>`, `<Import>`, `<TargetFramework>`, or any other
  dependency-affecting element **still require** the full scan.

The scanner fails closed on every error path (no diff_provider, unknown
file type, dependency-affecting edit).

## Version surfaces updated

| File                                                | Element          | New value   |
| --------------------------------------------------- | ---------------- | ----------- |
| `CivicSurvival/CivicSurvival.csproj`                | `<Version>`      | `0.3.25`    |
| `CivicSurvival/manifest.json`                       | `version_number` | `0.3.25`    |
| `CivicSurvival/Properties/PublishConfiguration.xml` | `<ModVersion>`   | `0.3.25`    |
| `CivicSurvival/Properties/PublishConfiguration.xml` | `<ChangeLog>`    | updated     |
| `CivicSurvival/Properties/CHANGELOG.md`             | `## v0.3.25`     | new section |

## Test results

- `tests/test_localization_keys.py`: **6/6 pass**
- `tests/test_ci_dependency_delta.py`: **33/35 pass** (2 pre-existing
  env failures: Ruby missing for YAML structural validation, cp1252
  codec — unrelated to this change)
- `ruff check`: clean
- `ruff format --check`: clean

## No gameplay changes

This release does not modify any of the 28 game domains
(`AirDefense`, `Narrative`, `PowerGrid`, `Waves`, `Blackout`, etc.).
All changes are in CI tooling and test infrastructure.

## Contributors

- @KooshaPari — release engineering, public-mirror curation
