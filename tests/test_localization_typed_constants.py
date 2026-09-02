"""Discipline test for the type-safe localization key catalog.

The static class ``L`` in ``CivicSurvival/Localization/LocalizationManager.cs``
declares typed constants for keys that code references type-safely
(e.g. ``LocalizationManager.Get(L.BLACKOUT_STARTED)``). The discipline
rule: **every L.* constant must exist as a key in every locale file**.

Without this test, a rename of ``L.SOME_KEY`` (or the underlying string
literal) is silently allowed to drift from the locale JSON. The runtime
falls back to the key string when a constant doesn't resolve, which
sneaks broken UI text past code review.

The test catches three classes of drift:

  1. **Constant claims a key but JSON doesn't have it** -- a typo, a
     deletion, or a missing locale update. This is a hard bug.
  2. **Constant references a key that has a variant shape** -- the key
     exists in JSON but with a ``_1``/``_2`` suffix that means it's
     meant for ``GetRandom``, not direct ``Get``. This is also a bug
     because direct ``Get`` on a variant key returns the variant text
     deterministically (no random selection).
  3. **No new L.* constants are added without a matching JSON key in
     all 3 locales** -- the test enforces a one-step discipline:
     adding a constant forces a JSON update in the same PR.

The test is intentionally read-only: it inspects the parsed C#
constant list via regex (no Roslyn, no compilation -- the public
mirror has no buildable project).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
LOCALES = ROOT / "CivicSurvival" / "Localization"
L_CLASS_FILE = LOCALES / "LocalizationManager.cs"
LOC_NAMES = ("en-US", "uk-UA", "zh-CN")

# Regex: capture ``public const string FOO = "FOO";`` inside the L class.
# The inner literal is the key (must match the constant name for sanity).
L_CONST_RE = re.compile(
    r'public\s+const\s+string\s+(?P<name>[A-Z][A-Z0-9_]+)\s*=\s*"(?P<key>[A-Z][A-Z0-9_]*)"\s*;'
)


def _load_locale(name: str) -> dict[str, str]:
    return json.loads((LOCALES / f"{name}.json").read_text(encoding="utf-8"))


def _parse_l_class() -> list[tuple[str, str]]:
    """Return [(constant_name, key_literal), ...] from the L class.

    Skips declarations outside the L class block by anchoring on the
    ``public static class L`` opener and the matching ``}``. For
    simplicity the regex scans the whole file -- the L class is the
    only ``public const string`` block in the project, and any false
    positives would surface in a CI run.
    """
    text = L_CLASS_FILE.read_text(encoding="utf-8")
    return [(m["name"], m["key"]) for m in L_CONST_RE.finditer(text)]


def _is_variant_key(key: str) -> bool:
    """A variant key ends in _<digits> (e.g. ``NEWS_FIRST_STRIKE_1``)."""
    return re.search(r"_\d+$", key) is not None


def test_l_class_constants_all_resolve_in_every_locale():
    """Every L.* constant must exist as a key in all 3 locale files."""
    constants = _parse_l_class()
    assert constants, "No L class constants parsed -- has LocalizationManager.cs been reformatted?"
    per_locale = {name: _load_locale(name) for name in LOC_NAMES}
    missing: dict[str, list[str]] = {}
    for cname, key in constants:
        for name, data in per_locale.items():
            if key not in data:
                missing.setdefault(name, []).append(f"{cname}->{key}")
    assert not missing, (
        "L class constants reference keys missing from one or more locales. "
        "Either the constant is wrong, or the locale JSON needs updating:\n"
        + "\n".join(f"  {name}: {keys}" for name, keys in missing.items())
    )


def test_l_class_constants_match_their_string_literal():
    """By convention every ``public const string FOO = "FOO";`` -- the
    constant name and the string literal must match. A mismatch is
    almost certainly a typo that would silently break callers using
    the literal name instead of the constant.
    """
    constants = _parse_l_class()
    mismatched = [(n, k) for n, k in constants if n != k]
    assert not mismatched, (
        "L class constants whose name doesn't match their string literal "
        "(typo?): " + ", ".join(f"{n}->{k}" for n, k in mismatched)
    )


def test_l_class_constants_are_not_variant_keys():
    """Direct ``Get`` on a numbered variant key bypasses randomization.

    If someone writes ``public const string FOO = "FOO_1";`` then every
    call site using ``L.FOO`` returns variant 1 every time -- defeating
    the purpose of the variant chain. This test rejects such constants.

    **Exception**: a constant may reference a variant key if its name
    explicitly carries the variant suffix (e.g. ``CHIRP_BLACKOUT_1``
    referencing key ``CHIRP_BLACKOUT_1``). These are deliberate
    deterministic-pick constants used when the game logic wants a
    specific variant rather than a random one. The invariant here is
    just: constant name and key string must be self-consistent.
    """
    constants = _parse_l_class()
    bad = [(n, k) for n, k in constants if _is_variant_key(k) and n != k]
    assert not bad, (
        "L class constants whose value is a variant key but name is not (typo / "
        "missing rename?): "
        + ", ".join(f"{n}->{k}" for n, k in bad)
        + ". Either the constant name must carry the variant suffix (FOO_1) or "
        "the constant must reference a non-variant key."
    )


def test_l_class_constant_count_is_stable():
    """Sanity guard: the L class should not grow or shrink by a large
    delta in a single PR. If it does, the PR author has either (a)
    done a legitimate large change and should bump this number with a
    comment, or (b) accidentally deleted a block of constants and
    needs to investigate.

    The current count is 56 (verified 2026-09-01, down from 60 after
    removing 4 dead base constants that pointed at missing variant
    keys). The bound is deliberately generous to allow legitimate
    cleanup PRs without false-positive CI failures.
    """
    constants = _parse_l_class()
    count = len(constants)
    assert 50 <= count <= 80, (
        f"L class has {count} constants; expected 50..80. "
        "If this is a deliberate bulk change, update the bound + this test's docstring."
    )


def test_l_class_section_comments_use_double_equals():
    """The L class uses ``// === Section ===`` comments to group
    constants. Drift here is cosmetic but worth catching -- a single
    ``// === Section`` (no closing) breaks the convention.
    """
    text = L_CLASS_FILE.read_text(encoding="utf-8")
    # Look for opening '=== ' without a closing ' ===' on the same line.
    bad_sections: list[str] = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if (
            "//" in stripped
            and "===" in stripped
            and not re.search(r"//\s*===\s*[^=].*===", stripped)
        ):
            bad_sections.append(f"L{i}: {stripped}")
    assert not bad_sections, (
        "L class section comments use a non-standard format. "
        "Expected '// === Section ===' (open AND close '===' on same line):\n"
        + "\n".join(bad_sections[:10])
    )
