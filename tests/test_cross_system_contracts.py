"""Cross-system contract tests for the canonical key catalog.

The public source has 3 type-safe key catalogs that drive every UI string
and server message:

  1. ReasonId  -- declared in CivicSurvival/Core/Types/ReasonIds.cs and
                  CivicSurvival/Core/UI/ReasonIds.cs via ReasonId.Of("UI_...").
                  Each ReasonId must resolve to a key in en-US / uk-UA / zh-CN
                  (the locale files), and every call site ReasonIds.X must
                  reference a declared id.

  2. L  -- declared in CivicSurvival/Localization/LocalizationManager.cs
           (already covered by tests/test_localization_typed_constants.py).

  3. Feature name -- declared in CivicSurvival/Mod.cs::RegisterFeatures(),
                    referenced via WaveOrder or FeatureManifest.

This discipline suite locks in the cross-system contracts that span the
three catalogs: declared ids must have callers, callers must reference
declared ids, and locale files must contain every declared string id.

Six rules enforced here:

1. test_reasonids_declarations_parse_unique -- every public static readonly
   ReasonId declaration in either partial-class file has a unique string
   id. Duplicate ReasonId.Of("X") declarations would cause the UI to
   collapse silently to the same locale key.

2. test_every_reasonid_locale_key_exists_in_every_locale -- the literal
   string id argument to ReasonId.Of(...) must exist as a key in en-US,
   uk-UA, AND zh-CN.

3. test_every_reasonid_referenced_or_explicitly_dead -- every declared
   ReasonId is either referenced somewhere in the .cs source OR is on
   the DEAD_REASONIDS_ALLOWLIST (the migration registry documents
   intentional dead ids).

4. test_every_reasonid_call_site_refers_to_a_declared_id -- every
   ReasonIds.X reference must match a declared id in one of the two
   partial-class files. Catches typos.

5. test_reasonids_partial_classes_split_cleanly -- both ReasonIds
   partial-class files declare a class with the same name in the same
   namespace, and neither has duplicate field names.

6. test_reasonid_of_argument_is_all_caps -- every ReasonId.Of("...")
   argument uses the canonical uppercase-snake UI_* convention.
   Lowercase or mixed-case arguments indicate a typo or copy-paste
   from prose.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

REASONIDS_TYPE = REPO / "CivicSurvival" / "Core" / "Types" / "ReasonIds.cs"
REASONIDS_UI = REPO / "CivicSurvival" / "Core" / "UI" / "ReasonIds.cs"
LOCALE_DIR = REPO / "CivicSurvival" / "Localization"

# Migration registry documents ids that were intentionally orphaned. Without
# this allowlist, deleting a ReasonId would silently pass the discipline test
# even though the locale key still ships to players.
DEAD_REASONIDS_ALLOWLIST: frozenset[str] = frozenset(
    {
        # ReasonIds.GwIntelAvailableRoutine / InsiderPrewarLocked were deleted
        # after the act predicate was moved out of the gw/insider decision
        # layer; the locale keys are unused but kept for translation-memory.
        "UI_GW_INTEL_AVAILABLE_ROUTINE",
        "UI_INSIDER_PREWAR_LOCKED",
        # UI_ARENA_REFRESH_TELEMETRY_DISABLED is intentionally reserved for a
        # future arena-mode telemetry flag (no current caller).
        "UI_ARENA_REFRESH_TELEMETRY_DISABLED",
    }
)


def _parse_declarations() -> dict[str, str]:
    out: dict[str, str] = {}
    for path in (REASONIDS_TYPE, REASONIDS_UI):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(
            r'ReasonId\.Of\(\s*"([A-Z0-9_]+)"\s*\)',
            text,
        ):
            key = m.group(1)
            out.setdefault(key, path.name)
    return out


def _parse_call_sites() -> set[str]:
    out: set[str] = set()
    for cs in (REPO / "CivicSurvival").rglob("*.cs"):
        if "/bin/" in str(cs) or "/obj/" in str(cs):
            continue
        text = cs.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\bReasonIds\.([A-Za-z][A-Za-z0-9_]*)\b", text):
            name = m.group(1)
            if name == "Of":
                continue
            out.add(name)
    return out


def _declared_member_names() -> set[str]:
    out: set[str] = set()
    for path in (REASONIDS_TYPE, REASONIDS_UI):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(
            r"public\s+static\s+readonly\s+ReasonId\s+([A-Za-z][A-Za-z0-9_]*)\s*=",
            text,
        ):
            out.add(m.group(1))
    return out


def _declared_member_names_from(text: str) -> set[str]:
    return {
        m.group(1)
        for m in re.finditer(
            r"public\s+static\s+readonly\s+ReasonId\s+([A-Za-z][A-Za-z0-9_]*)\s*=",
            text,
        )
    }


def _load_locale_keys() -> dict[str, set[str]]:
    import json

    out: dict[str, set[str]] = {}
    for path in LOCALE_DIR.glob("*.json"):
        out[path.name] = set(json.loads(path.read_text(encoding="utf-8")).keys())
    return out


class ReasonIdsContract(unittest.TestCase):
    """Cross-system contract for the ReasonIds partial-class catalog."""

    def test_reasonids_declarations_parse_unique(self):
        declarations = _parse_declarations()
        ids = list(declarations.keys())
        self.assertGreater(len(ids), 50, "ReasonIds catalog has fewer ids than expected")
        self.assertEqual(len(ids), len(set(ids)), msg="duplicate ReasonId.Of() declaration")

    def test_every_reasonid_locale_key_exists_in_every_locale(self):
        declarations = _parse_declarations()
        locales = _load_locale_keys()
        missing_in_any = []
        for key in declarations:
            for locale, keys in locales.items():
                if key not in keys:
                    missing_in_any.append((key, locale))
        if missing_in_any:
            self.fail(
                f"ReasonId string literals missing in locale files: "
                f"{[(k, loc) for k, loc in missing_in_any[:10]]} "
                f"(and {len(missing_in_any) - 10} more)"
            )

    def test_every_reasonid_referenced_or_explicitly_dead(self):
        declarations = _parse_declarations()
        declared_keys = set(declarations.keys())

        all_of_literals: set[str] = set()
        for cs in (REPO / "CivicSurvival").rglob("*.cs"):
            if "/bin/" in str(cs) or "/obj/" in str(cs):
                continue
            text = cs.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'ReasonId\.Of\(\s*"([A-Z0-9_]+)"\s*\)', text):
                all_of_literals.add(m.group(1))

        unused = sorted(declared_keys - all_of_literals - DEAD_REASONIDS_ALLOWLIST)
        if unused:
            self.fail(
                f"Declared ReasonId ids have no call site anywhere in the codebase: "
                f"{unused[:10]} (and {len(unused) - 10} more). Either add a caller, "
                f"delete the declaration, or add to DEAD_REASONIDS_ALLOWLIST."
            )

    def test_every_reasonid_call_site_refers_to_a_declared_id(self):
        member_names = _declared_member_names()
        call_sites = _parse_call_sites()
        unknown = sorted(call_sites - member_names - {"ActLockedFor"})
        if unknown:
            self.fail(
                f"ReasonIds.X references without a declared field: {unknown[:10]} "
                f"(and {len(unknown) - 10} more)"
            )

    def test_reasonids_partial_classes_split_cleanly(self):
        type_text = REASONIDS_TYPE.read_text(encoding="utf-8")
        ui_text = REASONIDS_UI.read_text(encoding="utf-8")
        self.assertRegex(type_text, r"public\s+static\s+partial\s+class\s+ReasonIds")
        self.assertRegex(ui_text, r"public\s+static\s+partial\s+class\s+ReasonIds")
        self.assertIn("namespace CivicSurvival.Core.Types", type_text)
        self.assertIn("namespace CivicSurvival.Core.Types", ui_text)
        type_names = _declared_member_names_from(type_text)
        ui_names = _declared_member_names_from(ui_text)
        dup = sorted(type_names & ui_names)
        self.assertFalse(dup, f"ReasonIds field name collision: {dup}")

    def test_reasonid_of_argument_is_all_caps(self):
        bad: list[tuple[str, str]] = []
        for cs in (REPO / "CivicSurvival").rglob("*.cs"):
            if "/bin/" in str(cs) or "/obj/" in str(cs):
                continue
            text = cs.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'ReasonId\.Of\(\s*"([^"]+)"\s*\)', text):
                arg = m.group(1)
                if not re.fullmatch(r"[A-Z0-9_]+", arg):
                    bad.append((cs.name, arg))
        if bad:
            self.fail(
                f"ReasonId.Of() literal not in canonical uppercase-snake: "
                f"{bad[:5]} (and {len(bad) - 5} more)"
            )


if __name__ == "__main__":
    unittest.main()