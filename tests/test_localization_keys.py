import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
LOCALES = ROOT / "CivicSurvival" / "Localization"
SRC_ROOT = ROOT / "CivicSurvival"
LOC_NAMES = ("en-US", "uk-UA", "zh-CN")

# Keys whose value is intentionally identical across every locale. This is
# the verified, hand-reviewed allowlist of legitimate exceptions: every entry
# is a proper noun, a raw number, a percent, a format template, or a single
# punctuation character. The audit discovered exactly this set; the test
# below asserts the runtime auto-discovery matches it -- any new identical
# key (drift) or any allowlist entry that no longer holds (rot) is rejected
# with a precise diff.
#
# If you need to add a new legitimate entry:
#   1. Confirm the value is genuinely untranslatable (proper noun / number
#      / format template / punctuation).
#   2. Update this set.
#   3. The test will fail until step 2 is complete, with a precise list of
#      keys that need to be added or removed.
LEGIT_IDENTICAL = {
    "DISTRICT_VIP",  # "VIP"
    "JOURNALIST_COUNT",  # "5"
    "MODAL_FATIGUE_DAYS_VALUE",  # "180"
    "MODAL_FATIGUE_NEWS_VALUE",  # "-60%"
    "MODAL_FIRST_STRIKE_TAX_VALUE",  # "-80%"
    "MODAL_VICTORY_DAYS_VALUE",  # "365"
    "MOD_NAME",  # "Civic Survival"
    "OVERRIDE_DISCORD",  # "Discord Webhook"
    "UI_ARENA_MONEY_VALUE",  # "+${0}"
    "UI_COST_FORMAT",  # "${0}k"
    "UI_DP_VIP",  # "VIP"
    "UI_MARKET_NA",  # "—" (em dash)
    "UI_WAVE_BADGE_V2",  # "V2"
}


def _auto_identical_keys() -> set[str]:
    """Compute the set of keys whose value is identical across all locales.

    This is the runtime ground truth. The test below compares it against the
    verified ``LEGIT_IDENTICAL`` allowlist; any divergence points to either
    (a) new untranslated residue slipping in, or (b) allowlist rot that
    needs cleanup.
    """
    data = {name: _load_locale(name) for name in LOC_NAMES}
    return {key for key in data["en-US"] if len({data[name][key] for name in LOC_NAMES}) == 1}


# Localized-file references inside .cs: Get("KEY"), L<T>.Key, HasKey("KEY"),
# GetPositiveInt("KEY"), GetRandom("PREFIX").
GET_RE = re.compile(r'\.(?:Get|HasKey)\(\s*"([A-Z][A-Z0-9_]+)"\s*\)')
T_RE = re.compile(r'\.Key\s*=\s*"([A-Z][A-Z0-9_]+)"')
INT_RE = re.compile(r'\.GetPositiveInt\(\s*"([A-Z][A-Z0-9_]+)"\s*\)')
RAND_RE = re.compile(r'\.GetRandom\(\s*"([A-Z][A-Z0-9_]+)"\s*\)')


def _load_locale(name: str) -> dict:
    return json.loads((LOCALES / f"{name}.json").read_text(encoding="utf-8"))


def _all_keys() -> set[str]:
    union: set[str] = set()
    for name in LOC_NAMES:
        union.update(_load_locale(name))
    return union


def test_locale_files_present_and_flat_string_maps():
    for name in LOC_NAMES:
        data = _load_locale(name)
        assert isinstance(data, dict), name
        for key, value in data.items():
            assert isinstance(key, str) and isinstance(value, str), (name, key)


def test_locale_keysets_are_identical():
    per_locale = {name: set(_load_locale(name)) for name in LOC_NAMES}
    reference = per_locale["en-US"]
    for name in LOC_NAMES:
        assert per_locale[name] == reference, (
            f"Locale {name} differs from en-US: missing={sorted(reference - per_locale[name])[:10]} "
            f"extra={sorted(per_locale[name] - reference)[:10]}"
        )


def test_no_untranslated_residue_across_locales():
    auto = _auto_identical_keys()
    missing = sorted(auto - LEGIT_IDENTICAL)
    extra = sorted(LEGIT_IDENTICAL - auto)
    assert not missing and not extra, (
        "Cross-locale identical keys drifted from the LEGIT_IDENTICAL allowlist.\n"
        f"  New identical keys (NOT in allowlist, possible untranslated residue): {missing}\n"
        f"  Allowlist entries no longer identical (rot, possibly translation now diverges): {extra}\n"
        "Update LEGIT_IDENTICAL in tests/test_localization_keys.py to acknowledge."
    )


def test_legit_identical_values_are_genuinely_untranslatable():
    """Sanity check: every entry in the allowlist must look like a proper noun,
    number, format template, or single punctuation character -- never a full
    sentence. This catches the case where someone adds a translatable key to
    the allowlist by mistake.
    """
    for name in LOC_NAMES:
        data = _load_locale(name)
        for key in LEGIT_IDENTICAL:
            value = data[key]
            assert len(value) <= 32, (
                f"Allowlist key {key!r} in locale {name} has value {value!r} longer than 32 chars -- "
                "looks like a translatable sentence, not a legitimate identical value."
            )
            assert " " not in value.strip() or value.strip() in {
                "Civic Survival",
                "Discord Webhook",
            }, (
                f"Allowlist key {key!r} in locale {name} has value {value!r} with internal whitespace -- "
                "looks like a phrase, not a proper noun or numeric template."
            )


def test_code_referenced_direct_keys_exist_in_all_locales():
    """Every string-literal key passed to Get/HasKey/GetPositiveInt in C# must
    resolve in every locale."""
    keys: set[str] = set()
    for path in SRC_ROOT.rglob("*.cs"):
        text = path.read_text(encoding="utf-8", errors="replace")
        keys.update(GET_RE.findall(text))
        keys.update(T_RE.findall(text))
        keys.update(INT_RE.findall(text))
    locale_keys = _all_keys()
    missing = sorted(keys - locale_keys)
    assert not missing, f"Code-referenced keys missing from locales: {missing[:20]}"


def test_getrandom_prefixes_have_complete_variant_sequences():
    """GetRandom("PREFIX") picks uniformly from PREFIX_1..PREFIX_N. Each prefix
    used in code must have a contiguous numbered variant set in every locale."""
    prefixes: set[str] = set()
    for path in SRC_ROOT.rglob("*.cs"):
        text = path.read_text(encoding="utf-8", errors="replace")
        prefixes.update(RAND_RE.findall(text))
    if not prefixes:
        return
    for name in LOC_NAMES:
        keys = _load_locale(name)
        for prefix in prefixes:
            variants = sorted(
                int(m.group(1))
                for key in keys
                for m in [re.fullmatch(rf"{re.escape(prefix)}_(\d+)", key)]
                if m
            )
            assert variants, f"Locale {name}: GetRandom prefix {prefix!r} has no _N variants"
            assert variants == list(range(1, len(variants) + 1)), (
                f"Locale {name}: GetRandom prefix {prefix!r} has non-contiguous "
                f"variants: {variants}"
            )
