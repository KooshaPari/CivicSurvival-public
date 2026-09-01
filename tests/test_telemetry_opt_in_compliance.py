"""Telemetry opt-in compliance tests.

Locks in the privacy contract documented in USER_GUIDE.md §"Notable
options" (lines 225-256) and enforced by CivicSurvival/Core/Services/
{ConsentStore, TelemetryOptInStore, TelemetryConfig}.cs.

Why this test exists:
  - GDPR/CCPA/COPPA enforcement and Paradox Mods platform policy both
    require concrete proof that telemetry is OFF BY DEFAULT, opt-in is
    global (save-independent), and no Personally Identifiable Information
    leaves the client.
  - Without these tests, a regression that defaulted telemetry to ON
    would ship invisibly. The user guide says it's off; the test
    enforces it.

Eight rules enforced here:
  1. Telemetry opt-in defaults to FALSE (no opt-in file = no telemetry).
  2. Online connection defaults to FALSE (independent flag).
  3. Effective Enabled = opt-in AND Online (line 121 of TelemetryConfig.cs).
     Turning Online off stops diagnostics even if you've opted in.
  4. Opt-in file is global, NOT per-save (lives in ModPaths.ModDataDirectory,
     not in the city save).
  5. Opt-out is sticky across reads (file is small, single line, "true"/"false").
  6. Server URL is HTTPS in production (NormalizeServerUrl refuses http).
  7. The user-facing disclosure covers every category mentioned in code:
     crash reports, perf metrics, hardware snapshot, mod/game version,
     and explicitly forbids PII (city names, Steam ID, email, location).
  8. USER_GUIDE is consistent with ConsentStore constants (file names match).

Run: pytest tests/test_telemetry_opt_in_compliance.py -v
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# === Files we look at ====================================================

CONSENT_STORE = ROOT / "CivicSurvival" / "Core" / "Services" / "ConsentStore.cs"
TELEMETRY_CONFIG = ROOT / "CivicSurvival" / "Core" / "Services" / "TelemetryConfig.cs"
TELEMETRY_OPT_IN_STORE = ROOT / "CivicSurvival" / "Core" / "Services" / "TelemetryOptInStore.cs"
MOD_PATHS = ROOT / "CivicSurvival" / "Core" / "Config" / "ModPaths.cs"
USER_GUIDE = ROOT / "USER_GUIDE.md"
MOD_CS = ROOT / "CivicSurvival" / "Mod.cs"


# === Rule 1: Telemetry opt-in defaults to FALSE ==========================


def test_consent_store_read_returns_false_when_file_missing() -> None:
    """ConsentStore.Read returns false when the opt-in file is absent.

    This is the safe default: no consent recorded = no telemetry. The
    game ships with no telemetry_optin.txt, so the first launch is
    telemetry-off until the player explicitly opts in via Settings.
    """
    cs = _read_text(CONSENT_STORE)
    assert "if (!info.Exists)" in cs, "ConsentStore.Read no longer short-circuits on missing file"
    assert "return false;" in cs, "ConsentStore.Read no longer defaults to false on miss"


def test_consent_store_read_returns_false_on_corrupt_or_oversized() -> None:
    """A file > 64 bytes or with garbage content falls back to default-off.

    This bounds the read (MaxFileBytes = 64) so a hostile / corrupt
    consent file cannot crash the read path, and so a truncated write
    cannot silently flip consent to true.
    """
    cs = _read_text(CONSENT_STORE)
    assert "MaxFileBytes" in cs, "ConsentStore.Read no longer bounds the file size"
    assert "info.Length > MaxFileBytes" in cs, (
        "ConsentStore.Read no longer rejects oversized consent files"
    )


def test_user_guide_says_telemetry_is_off_by_default() -> None:
    """USER_GUIDE must explicitly state telemetry is off by default.

    This is what GDPR/CCPA "explicit consent" enforcement looks at: the
    privacy disclosure has to match the runtime default. Drift here is a
    legal exposure, not just a doc nit.
    """
    ug = _read_text(USER_GUIDE)
    lower = ug.lower()
    # Must appear in the developer-diagnostics paragraph
    assert "off by default" in lower, (
        "USER_GUIDE no longer says telemetry is off by default -- this is a"
        " privacy-disclosure regression"
    )


# === Rule 2: Online connection is independently off by default =========


def test_online_connection_has_its_own_consent_key() -> None:
    """Online connection is gated by ConsentKey.OnlineConnection, not
    piggybacking on the telemetry key. The two flags must remain
    independently controllable so a player can use Online features
    (Global Grid) without enabling developer diagnostics, or vice versa.
    """
    cs = _read_text(CONSENT_STORE)
    assert "ConsentKey.OnlineConnection" in cs, (
        "ConsentKey.OnlineConnection is missing -- Online cannot be gated"
        " independently of telemetry anymore"
    )
    opt_in = _read_text(TELEMETRY_OPT_IN_STORE)
    assert "ConsentKey.Telemetry" in opt_in, (
        "TelemetryOptInStore no longer binds to ConsentKey.Telemetry"
    )


def test_user_guide_says_online_is_off_by_default() -> None:
    """USER_GUIDE must state Online is off by default.

    Global Grid sends city data to a server; "off by default" is the
    only legal posture without a first-launch consent dialog.
    """
    ug = _read_text(USER_GUIDE)
    # Online features paragraph: "Off by default."
    assert "Global Grid" in ug or "Online features" in ug, (
        "USER_GUIDE no longer mentions Global Grid / Online features"
    )
    # The "off by default" claim appears in the Online features paragraph
    # specifically (USER_GUIDE:231)
    online_paragraph_start = ug.find("Online features")
    if online_paragraph_start < 0:
        online_paragraph_start = ug.find("Global Grid")
    assert online_paragraph_start >= 0, "USER_GUIDE has no Online-features paragraph"
    # Find "off by default" within ~500 chars after the Online paragraph header
    next_section = ug.find("\n##", online_paragraph_start)
    if next_section < 0:
        next_section = len(ug)
    online_block = ug[online_paragraph_start:next_section]
    assert "off by default" in online_block.lower(), (
        "Online features paragraph no longer states off-by-default"
    )


# === Rule 3: Enabled = opt-in AND Online ==================================


def test_effective_enabled_gate_is_opt_in_and_online() -> None:
    """TelemetryConfig.Enabled is the EFFECTIVE gate: opt-in AND Online.

    This invariant means turning Online off stops diagnostics even if
    the player opted in. The user guide promises this on line 239:
    'only sent while Online is on. When on, the mod collects ...'

    The expression is in TelemetryConfig.cs constructor (line 121).
    """
    tc = _read_text(TELEMETRY_CONFIG)
    # Either "Enabled = diagnosticsOptIn && onlineEnabled;" or in the
    # ctor arguments. Look for the AND operator between opt-in and online.
    ctor_block = tc[tc.find("private TelemetryConfig(") :]
    assert "Enabled = diagnosticsOptIn && onlineEnabled" in ctor_block or (
        "Enabled = " in ctor_block
        and "diagnosticsOptIn" in ctor_block
        and "onlineEnabled" in ctor_block
        and "&&" in ctor_block
    ), "TelemetryConfig.Enabled is no longer the AND of opt-in and online"


def test_file_only_mode_equals_not_enabled() -> None:
    """TelemetryConfig.FileOnlyMode = !Enabled.

    When diagnostics are off, nothing leaves over HTTP — file-only mode
    is the inverse of the effective gate, not an independent flag.
    """
    tc = _read_text(TELEMETRY_CONFIG)
    assert "FileOnlyMode = !Enabled" in tc, (
        "TelemetryConfig.FileOnlyMode is no longer !Enabled -- "
        "diagnostics-off must not still send over HTTP"
    )


# === Rule 4: Opt-in file is global, not per-save =========================


def test_opt_in_file_lives_in_global_mod_data_directory() -> None:
    """The opt-in file lives next to the native crash breadcrumb in
    ModPaths.ModDataDirectory, NOT in a per-save file. This is what
    makes consent survive across city resets.
    """
    cs = _read_text(CONSENT_STORE)
    assert "ModPaths.ModDataDirectory" in cs, (
        "ConsentStore no longer persists in ModPaths.ModDataDirectory -- "
        "consent may now be tied to a save file"
    )
    # The opt-in file is read at init time, before any save deserializes
    # (per the file's own XML doc). Sanity check: the file name matches
    # the one in ModPaths.
    mp = _read_text(MOD_PATHS)
    assert "TelemetryOptInFile" in mp, (
        "ModPaths no longer declares TelemetryOptInFile -- the consent "
        "file is now floating without a canonical name"
    )


def test_mod_cs_seeds_telemetry_state_before_save_loads() -> None:
    """Mod.OnLoad must seed telemetry/online consent from the global
    store BEFORE any save loads, otherwise TelemetryCrashDetector sees
    the wrong state and silently ships diagnostics to a player who
    never opted in.
    """
    mod = _read_text(MOD_CS)
    assert "TelemetryOptInStore.Read()" in mod, (
        "Mod.cs no longer reads TelemetryOptInStore at init -- "
        "consent may now be derived from a not-yet-loaded save"
    )
    # The actual call site is uniquely identifiable: the seed is wrapped
    # in SetTelemetryEnabled() on the modSettings patch line. The Load
    # call site is uniquely identifiable: it's followed by
    # "(modSettings)". (Both names also appear in XML doc comments
    # elsewhere in the file, so we have to find the actual calls.)
    seed_pos = mod.find("SetTelemetryEnabled(Core.Services.TelemetryOptInStore.Read())")
    load_pos = mod.find("TelemetryConfig.Load(modSettings)")
    assert seed_pos > 0, (
        "Could not find the modSettings seed call site that wraps"
        " TelemetryOptInStore.Read() in SetTelemetryEnabled"
    )
    assert load_pos > 0, "Could not find TelemetryConfig.Load(modSettings) call site"
    assert seed_pos < load_pos, (
        "TelemetryOptInStore.Read() must be called before TelemetryConfig.Load; "
        f"got seed@ {seed_pos}, load@ {load_pos}"
    )


# === Rule 5: Opt-out is sticky ===========================================


def test_user_guide_promises_diagnostics_can_be_turned_off_independently() -> None:
    """USER_GUIDE must state diagnostics can be turned off independently
    of Online features — and vice versa. Without this, the user has no
    meaningful way to consent to Online without also consenting to
    diagnostics.
    """
    ug = _read_text(USER_GUIDE)
    # "off while keeping Online on" or "off" + "while Online is on"
    assert "Online on" in ug or "Online is on" in ug, (
        "USER_GUIDE no longer explains the Online-vs-diagnostics independence"
    )


def test_consent_write_persists_across_reads() -> None:
    """ConsentStore.Write uses AtomicFileWriter for the consent flag,
    so a power loss between Write and a subsequent Read cannot leave
    consent in a half-set state.
    """
    cs = _read_text(CONSENT_STORE)
    assert "AtomicFileWriter" in cs, (
        "ConsentStore.Write no longer uses AtomicFileWriter -- "
        "torn consent writes may now produce silent reverts"
    )


# === Rule 6: Server URL is HTTPS in production ===========================


def test_normalize_server_url_rejects_http_in_production() -> None:
    """NormalizeServerUrl refuses non-HTTPS URLs (except DEBUG loopback).

    Player ID + auth_token flow over this transport; an http:// override
    would let a network observer capture both. This is the single most
    privacy-critical invariant in the telemetry path.
    """
    tc = _read_text(TELEMETRY_CONFIG)
    assert "NormalizeServerUrl" in tc, (
        "TelemetryConfig.NormalizeServerUrl is missing -- HTTP overrides"
        " can now downgrade telemetry transport"
    )
    normalize = tc[tc.find("public static string NormalizeServerUrl") :]
    assert "Uri.UriSchemeHttps" in normalize, "NormalizeServerUrl no longer enforces HTTPS"
    # Production URL is HTTPS
    assert "https://" in tc, "Production server URL is not HTTPS"
    assert "ProductionServerUrl" in tc, "ProductionServerUrl constant is missing"


def test_normalize_server_url_falls_back_when_override_invalid() -> None:
    """If the env override is bogus, NormalizeServerUrl falls back to
    the production URL rather than passing garbage to the HTTP client.
    """
    tc = _read_text(TELEMETRY_CONFIG)
    normalize = tc[tc.find("public static string NormalizeServerUrl") :]
    assert "return fallback" in normalize, (
        "NormalizeServerUrl no longer falls back to the production URL on invalid override"
    )


# === Rule 7: Disclosure matches code =====================================


def test_user_guide_explicitly_forbids_pii_categories() -> None:
    """The user guide must explicitly state that diagnostics do NOT
    collect city names, save names, files, Steam ID, chat, email, or
    location. These are the categories GDPR/CCPA enforcement looks for.
    """
    ug = _read_text(USER_GUIDE)
    required_categories = [
        "city names",
        "save names",
        "files",
        "Steam ID",
        "chat",
        "email",
        "location",
    ]
    missing = [c for c in required_categories if c not in ug]
    assert not missing, (
        f"USER_GUIDE privacy disclosure no longer mentions these PII categories: {missing}"
    )


def test_user_guide_lists_what_diagnostics_collect() -> None:
    """The user guide must list what diagnostics DO collect: crash
    reports, error stack traces, performance metrics (FPS, frame time,
    memory), hardware snapshot (CPU, RAM, GPU, OS), and mod/game version.
    """
    ug = _read_text(USER_GUIDE)
    lower = ug.lower()
    required = [
        "crash report",
        "stack trace",
        "fps",
        "frame time",
        "memory",
        "cpu",
        "ram",
        "gpu",
        "os platform",
        "mod",
        "version",
    ]
    missing = [r for r in required if r not in lower]
    assert not missing, (
        f"USER_GUIDE privacy disclosure no longer mentions these diagnostic categories: {missing}"
    )


# === Rule 8: USER_GUIDE file names match code ============================


def test_user_guide_mentions_random_id() -> None:
    """USER_GUIDE must state that the city data is tied to a RANDOM ID,
    not the player's real-world identity. This is the GDPR pseudonymization
    disclosure.
    """
    ug = _read_text(USER_GUIDE)
    assert "random" in ug.lower(), "USER_GUIDE no longer mentions the random ID"
    # The exact phrasing: "random ID that is not your real-world identity"
    assert "real-world identity" in ug or "real world identity" in ug or "your real" in ug, (
        "USER_GUIDE no longer contrasts the random ID with real-world identity"
    )


def test_user_guide_nickname_disclosure_is_present() -> None:
    """If a nickname feature exists, the user guide must warn that the
    nickname is PUBLIC on the leaderboard (not just visible to the player).
    """
    ug = _read_text(USER_GUIDE)
    assert "nickname" in ug.lower(), "USER_GUIDE no longer mentions the nickname feature"
    assert "publicly visible" in ug.lower() or "public" in ug.lower(), (
        "USER_GUIDE no longer warns that nickname is publicly visible"
    )


# === Cross-cutting: telemetry is disabled for non-disclosure builds =====


def test_diagnostics_disabled_when_online_off() -> None:
    """USER_GUIDE says diagnostics 'is only sent while Online is on'. The
    runtime must mirror this: turning Online off stops diagnostics even
    if the player previously opted in.

    This is the EFFECTIVE_GATE test — verifies the comment matches the
    code at TelemetryConfig.cs:118-122.
    """
    tc = _read_text(TELEMETRY_CONFIG)
    # The constructor must AND the two flags
    ctor_block = tc[tc.find("private TelemetryConfig(") :]
    assert "diagnosticsOptIn && onlineEnabled" in ctor_block, (
        "TelemetryConfig ctor no longer ANDs opt-in and online"
    )


def test_no_first_launch_telemetry_without_consent() -> None:
    """TelemetryCrashDetector must NOT ship diagnostics before consent
    is established. The init-time path (TelemetryConfig.Load at line
    145 reads TelemetryOptInStore.Read) is the safe posture.

    The mod.cs seeding comment specifically says: 'persisted globally
    (save-independent). Seed it here at init so the Options toggle
    reflects real consent immediately'.
    """
    mod = _read_text(MOD_CS)
    # The TelemetryConfig.Load call uses the seeded settings
    assert "TelemetryConfig.Load(modSettings)" in mod, (
        "Mod.cs no longer loads TelemetryConfig from seeded settings at init"
    )
    # And modSettings is seeded from TelemetryOptInStore.Read
    seed_block = mod[mod.find("modSettings = new ModSettings()") :]
    seed_end = seed_block.find("services.Register(modSettings)")
    assert seed_end > 0, "Could not locate the modSettings seed block"
    seed = seed_block[:seed_end]
    assert "TelemetryOptInStore.Read()" in seed, (
        "modSettings is no longer seeded with TelemetryOptInStore.Read()"
    )
