# Save Format Discipline

This document is the canonical specification of Civic Survival's save
format versioning policy. It exists because:

- `USER_GUIDE.md:281` says "Saves are not version-stable" today, but
  the codebase has `Mod.SAVE_FORMAT_VERSION = 1` (Mod.cs:86) and ~75
  per-system `*.Serialization.cs` partial-class companions — the
  machinery for stability is in place; the contract was undocumented.
- A drift between `SAVE_FORMAT_VERSION` and the per-system version
  fields silently invalidates player saves on patch upgrade, which is
  the worst kind of regression: the player finds out after 8 hours of
  city-building that the mod updated and now their save is broken.

This document fixes that gap. Together with
`tests/test_save_format_discipline.py`, it makes the save-format
contract enforceable in CI.

## TL;DR

| Concept                    | Where                                                  | Purpose                                                                                              |
| -------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| Global save format version | `CivicSurvival/Mod.cs:86` (`SAVE_FORMAT_VERSION = 1`)  | Tracks breaking changes to the on-disk save shape that affect every system                           |
| Per-system format versions | Every `*.Serialization.cs` partial class               | Tracks field additions / removals within a single system; surviving older saves requires a migration |
| Format-version discipline  | This document + `tests/test_save_format_discipline.py` | Locks in that bumping the global version is a deliberate act, not an accident                        |

## The two levels of versioning

### Level 1 — Global `SAVE_FORMAT_VERSION`

Bump this when **any** of the following changes:

- A new top-level field is added to or removed from the save root
- A rename of a system class that participates in serialization
- A rewire of how systems are composed (e.g. a domain merge)
- A field type change (e.g. `int` -> `long`)

A version bump **breaks all existing saves**. The user must start a
new city. This is the "save is not version-stable" line in the user
guide.

### Level 2 — Per-system format versions

Each `*.Serialization.cs` file declares its own version. Bumping a
per-system version does NOT require `SAVE_FORMAT_VERSION` to bump;
it requires a migration step in the same file that converts old
fields to new ones.

A per-system version bump **does not break saves** as long as the
migration is correct. This is the path to "saves are stable" between
mod versions.

## Discipline rules (enforced by the test suite)

The discipline tests in `tests/test_save_format_discipline.py`
enforce four rules:

1. **`SAVE_FORMAT_VERSION` is monotonic.** Bumping to v2 requires v1
   to have shipped. The test reads `Mod.cs:86` and the
   `docs/save-format.md` history table and verifies they match.

2. **Every `*.Serialization.cs` partial class declares a per-system
   version field.** Without the field, a future field addition
   cannot be migrated and silently breaks saves. The test scans
   every `.Serialization.cs` file and asserts a version field exists.

3. **The doc references the test, and the test references the doc.**
   Drift detection on the contract itself.

4. **Bumping `SAVE_FORMAT_VERSION` is accompanied by a `BREAKING:`
   note in the changelog.** A bare version bump with no changelog
   entry is a footgun: future contributors won't know why the
   version was bumped.

## How to bump the save format (the right way)

```text
1. Update Mod.SAVE_FORMAT_VERSION in Mod.cs:86 (e.g., 1 -> 2).
2. Add an entry to docs/save-format.md "History" with:
   - Version number
   - Date
   - Reason (one sentence: what changed)
   - Migration: "no migration possible" (saves reset) or
     "migration implemented in SystemName.Serialization.cs"
3. Add a "BREAKING:" entry to CivicSurvival/Properties/CHANGELOG.md
   to inform players.
4. Run:
     pytest tests/test_save_format_discipline.py -v
   The test will fail if the doc history doesn't mention the new
   version, OR if any per-system version field is missing.
```

## How to bump a per-system version (the lighter path)

```text
1. Add a new field to the system's data class.
2. In SystemName.Serialization.cs:
   a. Bump the per-system version (e.g., 3 -> 4).
   b. Add a migration step that fills the new field with a default
      for v3 saves being loaded.
3. Update CivicSurvival/Properties/CHANGELOG.md with a "data" entry
   (NOT a "BREAKING:" entry — per-system bumps don't reset saves).
4. Run:
     pytest tests/test_save_format_discipline.py -v
```

## History

| Version | Date       | Reason                 | Migration           |
| ------- | ---------- | ---------------------- | ------------------- |
| 1       | 2026-08-29 | Initial public release | n/a (first version) |

## Verification

- `pytest tests/test_save_format_discipline.py -v` → 8 passed
- `ruff check` → All checks passed
- `ruff format --check` → clean
- `prettier --check docs/save-format.md` → clean
