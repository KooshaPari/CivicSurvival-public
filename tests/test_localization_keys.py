import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
LOCALES = ROOT / "CivicSurvival" / "Localization"
SRC_ROOT = ROOT / "CivicSurvival"
LOC_NAMES = ("en-US", "uk-UA", "zh-CN")

# Keys whose value is intentionally identical across every locale. Audit
# discovered this exact 13-key set; any cross-locale identical key not in
# this list is untranslated residue. All 13 are proper nouns, raw numbers,
# or format templates — none are translatable sentences.
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
    data = {name: _load_locale(name) for name in LOC_NAMES}
    for key in data["en-US"]:
        values = {data[name][key] for name in LOC_NAMES}
        if len(values) > 1:
            continue
        assert key in LEGIT_IDENTICAL, (
            f"Key {key!r} is identical across all locales (={next(iter(values))!r}) "
            f"but is not in the LEGIT_IDENTICAL allowlist — likely untranslated residue."
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
            assert variants, (
                f"Locale {name}: GetRandom prefix {prefix!r} has no _N variants"
            )
            assert variants == list(range(1, len(variants) + 1)), (
                f"Locale {name}: GetRandom prefix {prefix!r} has non-contiguous "
                f"variants: {variants}"
            )
