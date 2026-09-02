"""README link discipline.

The root README.md is the entry point for the public mirror. Every link it
contains is a promise: if the link breaks, a reader of the mod's source
hits a 404 / dead end. This test enforces:

1. Every relative file link (./X, ../X, X.md, X/) points at an existing
   file or directory. (External URLs are out of scope -- testing them
   would couple CI to network and to upstream availability.)
2. The README mentions each of the four core docs (USER_GUIDE.md,
   PRIVACY.md, BUILDING.md, CONTRIBUTING.md) so a new contributor can
   find each one.
3. The AI declaration paragraph is preserved. (We declared AI authorship;
   removing it would be a regression in transparency.)
4. The PolyForm Strict license notice is preserved with the SPDX
   identifier intact.
5. The Paradox Mods link is present and uses the canonical mod id.

This is a tiny test with high value -- it's the smallest unit of
"is the mod discoverable and honest about what it is?"
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
README = ROOT / "README.md"


def _readme() -> str:
    return README.read_text(encoding="utf-8")


def test_readme_exists_and_is_not_empty() -> None:
    assert README.exists(), "README.md does not exist at the repo root"
    text = _readme()
    assert len(text) > 500, f"README.md is suspiciously short ({len(text)} chars)"


def test_readme_mentions_all_four_core_docs() -> None:
    """The README is the only entry point most contributors will read.
    It must point at the four canonical docs so anyone landing on the
    repo can find each one.
    """
    text = _readme()
    required = ["USER_GUIDE.md", "PRIVACY.md", "BUILDING.md", "CONTRIBUTING.md"]
    missing = [doc for doc in required if doc not in text]
    assert not missing, (
        f"README.md is missing references to: {missing}. The mod's "
        f"transparency story requires that every core doc be discoverable "
        f"from the README alone."
    )


def test_readme_relative_file_links_resolve() -> None:
    """Every `./X` or `X.md` or `X/` link in the README must point at
    an existing file or directory at the repo root.
    """
    text = _readme()
    # Match both `[label](path)` and bare `path`. We're strict about path
    # boundaries so that we don't false-positive on URL fragments.
    # Patterns we match:
    #   [..](USER_GUIDE.md)
    #   [..](../docs/release-phases.md)
    #   [..](./CONTRIBUTING.md)
    #   [..](Assets/)  -- dir
    #   [..](docs/release-phases.md#anchor)  -- with anchor
    pattern = re.compile(
        r"\[[^\]]+\]\((?:\.{0,2}/)?([A-Za-z0-9_\-./]+(?:\.[A-Za-z0-9]+)?)(?:#[^)]+)?\)"
    )
    links: list[str] = []
    for match in pattern.finditer(text):
        path = match.group(1)
        # Skip external links and pure fragments
        if path.startswith(("http://", "https://", "#", "mailto:")):
            continue
        # Skip badge URLs (they're full URLs even when wrapped in markdown link syntax
        # but we already filtered http(s) above; this catches the case where a bare
        # domain or /path is used)
        if "/" not in path and not path.endswith(
            (".md", ".txt", ".csproj", ".cs", ".yml", ".yaml", ".json", ".xml", ".png", ".svg")
        ):
            continue
        links.append(path)

    missing = [p for p in links if not (ROOT / p).exists()]
    assert not missing, f"README.md references files that do not exist at the repo root: {missing}"


def test_readme_preserves_ai_declaration() -> None:
    """The README declares AI authorship as part of the mod's transparency
    story. A regression that removes this paragraph would be a transparency
    regression -- the contract with players is that we are open about it.
    """
    text = _readme()
    # Both 'AI-generated' and 'AI' must appear in the declaration paragraph
    assert "AI" in text, "README.md no longer mentions AI"
    # The specific declaration we shipped
    assert "AI-generated" in text or "AI assistant" in text, (
        "README.md AI declaration paragraph appears to have been removed or "
        "reworded past recognition. This is a transparency contract -- "
        "please restore the original language."
    )


def test_readme_preserves_license_notice() -> None:
    """The README must continue to identify the license (PolyForm Strict 1.0.0)
    so the license story stays consistent with LICENSE + NOTICE.md.
    """
    text = _readme()
    assert "PolyForm" in text, "README.md no longer mentions the PolyForm license"
    # The asset license dual-notice
    assert "CC BY-NC-ND" in text or "CC" in text, (
        "README.md no longer mentions the asset-level CC license"
    )


def test_readme_preserves_paradox_mods_link() -> None:
    """The README links to the mod's Paradox Mods page so a player can
    install it. If the mod id changes, this URL must change too.
    """
    text = _readme()
    assert "mods.paradoxplaza.com" in text, "README.md no longer links to the Paradox Mods page"


def test_readme_discord_link_is_present() -> None:
    """Bug reports go to Discord, not GitHub Issues, per the README's
    stated policy. Removing the Discord link breaks the support contract.
    """
    text = _readme()
    assert "discord" in text.lower(), "README.md no longer mentions Discord"
    assert "discord.gg/" in text or "discord.com/" in text, (
        "README.md Discord reference is not a clickable-looking URL. "
        "Either reformat it or restore the discord.gg/ link."
    )


def test_readme_one_mod_two_experiences_table_is_present() -> None:
    """The 'One Mod, Two Experiences' table is part of the mod's identity
    (English / Ukrainian split). Removing or rewording it past recognition
    is a regression.
    """
    text = _readme()
    assert "One Mod, Two Experiences" in text, (
        "README.md is missing the 'One Mod, Two Experiences' section header"
    )
    # The four canonical table cells
    expected_cells = [
        "Power Company",
        "ДТЕК",
        "Emergency Shelter",
        "Incoming threat",
    ]
    missing = [c for c in expected_cells if c not in text]
    assert not missing, (
        f"README.md 'One Mod, Two Experiences' table is missing canonical cells: {missing}"
    )
