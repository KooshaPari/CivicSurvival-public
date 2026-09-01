"""Tests for scripts/release.py: lock in atomic version bumps across all 4 surfaces."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release  # noqa: E402  (path-mutated import)

CSPROJ_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <Version>{version}</Version>
    <Description>Civic Survival</Description>
  </PropertyGroup>
</Project>
"""

MANIFEST_TEMPLATE = """{{
  "name": "CivicSurvival",
  "version_number": "{version}",
  "website_url": "https://example.com",
  "description": "test",
  "dependencies": []
}}
"""

XML_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Publish>
  <ModId Value="147665" />
  <ModVersion Value="{version}" />
  <GameVersion Value="*" />
  <ChangeLog>{summary}</ChangeLog>
</Publish>
"""

CHANGELOG_TEMPLATE = """# Civic Survival — Changelog

Player-facing release notes shipped with the Paradox Mods build.

## v{version} — Initial release

- First entry.

---
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Build a fake repo containing all 4 release surfaces at version 0.3.25."""
    (tmp_path / "CivicSurvival").mkdir()
    (tmp_path / "CivicSurvival" / "Properties").mkdir()
    (tmp_path / "CivicSurvival" / "CivicSurvival.csproj").write_text(
        CSPROJ_TEMPLATE.format(version="0.3.25"), encoding="utf-8"
    )
    (tmp_path / "CivicSurvival" / "manifest.json").write_text(
        MANIFEST_TEMPLATE.format(version="0.3.25"), encoding="utf-8"
    )
    (tmp_path / "CivicSurvival" / "Properties" / "PublishConfiguration.xml").write_text(
        XML_TEMPLATE.format(version="0.3.25", summary="Initial release."),
        encoding="utf-8",
    )
    (tmp_path / "CivicSurvival" / "Properties" / "CHANGELOG.md").write_text(
        CHANGELOG_TEMPLATE.format(version="0.3.25"), encoding="utf-8"
    )
    return tmp_path


def _paths(repo: Path) -> release.ReleasePaths:
    return release.ReleasePaths.for_repo(repo)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Version parsing
# ---------------------------------------------------------------------------


def test_version_parse_accepts_canonical_semver():
    assert release.Version.parse("0.3.25") == release.Version(0, 3, 25)


def test_version_parse_strips_whitespace():
    assert release.Version.parse("  1.2.3  ") == release.Version(1, 2, 3)


@pytest.mark.parametrize(
    "bad", ["", "1.2", "1.2.3.4", "1.2.x", "v1.2.3", "1.-2.3", "  "]
)
def test_version_parse_rejects_invalid_inputs(bad: str):
    with pytest.raises(ValueError, match="invalid version"):
        release.Version.parse(bad)


def test_version_ordering_supports_bump_comparison():
    assert release.Version.parse("0.3.26") > release.Version.parse("0.3.25")
    assert release.Version.parse("1.0.0") > release.Version.parse("0.99.99")
    assert release.Version.parse("0.3.25") == release.Version.parse("0.3.25")


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------


def test_current_version_reads_all_three_program_surfaces(repo: Path):
    assert release.read_current_version(_paths(repo)) == release.Version(0, 3, 25)


def test_current_version_returns_none_when_csproj_drifts(repo: Path):
    paths = _paths(repo)
    (paths.csproj).write_text(CSPROJ_TEMPLATE.format(version="9.9.9"), encoding="utf-8")
    assert release.read_current_version(paths) is None


def test_current_version_returns_none_when_manifest_drifts(repo: Path):
    paths = _paths(repo)
    data = json.loads(_read(paths.manifest))
    data["version_number"] = "9.9.9"
    paths.manifest.write_text(json.dumps(data), encoding="utf-8")
    assert release.read_current_version(paths) is None


def test_current_version_returns_none_when_xml_mod_version_drifts(repo: Path):
    paths = _paths(repo)
    text = _read(paths.xml)
    text = text.replace('<ModVersion Value="0.3.25"', '<ModVersion Value="9.9.9"')
    paths.xml.write_text(text, encoding="utf-8")
    assert release.read_current_version(paths) is None


# ---------------------------------------------------------------------------
# Bump command -- atomic, fail-closed
# ---------------------------------------------------------------------------


def test_bump_writes_all_four_surfaces_atomically(
    repo: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(repo)
    code = release.main(
        [
            "--repo",
            str(repo),
            "bump",
            "--version",
            "0.3.26",
            "--title",
            "Performance and bug fixes",
            "--summary",
            "Performance and bug fixes.",
            "--bullet",
            "Fix A",
            "--bullet",
            "Tune B",
        ]
    )
    assert code == 0
    paths = _paths(repo)

    assert release.read_csproj_version(paths) == release.Version(0, 3, 26)
    assert release.read_manifest_version(paths) == release.Version(0, 3, 26)
    assert release.read_xml_mod_version(paths) == release.Version(0, 3, 26)
    assert release.read_current_version(paths) == release.Version(0, 3, 26)

    xml_text = _read(paths.xml)
    assert "<ChangeLog>Performance and bug fixes.</ChangeLog>" in xml_text

    changelog_text = _read(paths.changelog)
    new_section_match = re.search(
        r"^## v0\.3\.26 — Performance and bug fixes\s*$",
        changelog_text,
        re.MULTILINE,
    )
    assert new_section_match is not None
    after = changelog_text[new_section_match.end() :]
    assert "- Fix A" in after
    assert "- Tune B" in after


def test_bump_rejects_invalid_version_format(repo: Path):
    code = release.main(
        [
            "--repo",
            str(repo),
            "bump",
            "--version",
            "0.3",
            "--title",
            "x",
            "--summary",
            "x",
            "--bullet",
            "x",
        ]
    )
    assert code == 2


def test_bump_refuses_when_version_is_not_strictly_greater(repo: Path):
    for bad in ("0.3.25", "0.2.99", "0.3.24"):
        code = release.main(
            [
                "--repo",
                str(repo),
                "bump",
                "--version",
                bad,
                "--title",
                "x",
                "--summary",
                "x",
                "--bullet",
                "x",
            ]
        )
        assert code == 2, f"version {bad} should have been rejected"


def test_bump_refuses_when_surfaces_already_inconsistent(repo: Path):
    paths = _paths(repo)
    # Drift the manifest before bumping.
    data = json.loads(_read(paths.manifest))
    data["version_number"] = "9.9.9"
    paths.manifest.write_text(json.dumps(data), encoding="utf-8")

    code = release.main(
        [
            "--repo",
            str(repo),
            "bump",
            "--version",
            "0.3.26",
            "--title",
            "x",
            "--summary",
            "x",
            "--bullet",
            "x",
        ]
    )
    assert code == 2
    # Neither the csproj nor the XML should have been touched by the failed
    # bump attempt, and the drifted manifest must remain at its drifted value
    # (the script never writes to a file once it has decided to fail).
    assert release.read_csproj_version(paths) == release.Version(0, 3, 25)
    assert release.read_xml_mod_version(paths) == release.Version(0, 3, 25)
    assert release.read_manifest_version(paths) == release.Version(9, 9, 9)


def test_bump_requires_at_least_one_bullet(repo: Path):
    code = release.main(
        [
            "--repo",
            str(repo),
            "bump",
            "--version",
            "0.3.26",
            "--title",
            "x",
            "--summary",
            "x",
        ]
    )
    assert code == 2


def test_bump_requires_non_empty_title(repo: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(repo)
    paths = _paths(repo)
    code = release.main(
        [
            "--repo",
            str(repo),
            "bump",
            "--version",
            "0.3.26",
            "--title",
            "   ",
            "--summary",
            "x",
            "--bullet",
            "x",
        ]
    )
    assert code == 2
    assert release.read_csproj_version(paths) == release.Version(0, 3, 25)


# ---------------------------------------------------------------------------
# Verify / current commands
# ---------------------------------------------------------------------------


def test_cmd_current_prints_version_when_consistent(
    repo: Path, capsys: pytest.CaptureFixture[str]
):
    code = release.main(["--repo", str(repo), "current"])
    out = capsys.readouterr().out
    assert code == 0
    assert out.strip() == "0.3.25"


def test_cmd_current_exits_one_when_inconsistent(
    repo: Path, capsys: pytest.CaptureFixture[str]
):
    paths = _paths(repo)
    text = _read(paths.csproj)
    text = text.replace("<Version>0.3.25</Version>", "<Version>9.9.9</Version>")
    paths.csproj.write_text(text, encoding="utf-8")

    code = release.main(["--repo", str(repo), "current"])
    captured = capsys.readouterr()
    assert code == 1
    assert "inconsistent" in captured.err


def test_cmd_verify_exits_zero_on_consistency(repo: Path):
    assert release.main(["--repo", str(repo), "verify"]) == 0


def test_cmd_verify_exits_one_on_drift(repo: Path, capsys: pytest.CaptureFixture[str]):
    paths = _paths(repo)
    data = json.loads(_read(paths.manifest))
    data["version_number"] = "9.9.9"
    paths.manifest.write_text(json.dumps(data), encoding="utf-8")

    code = release.main(["--repo", str(repo), "verify"])
    captured = capsys.readouterr()
    assert code == 1
    assert "mismatch" in captured.err


# ---------------------------------------------------------------------------
# End-to-end via subprocess against a real git repo
# ---------------------------------------------------------------------------


def test_cli_end_to_end_via_subprocess(tmp_path: Path):
    """Run the script as a real CLI against a tmp git repo with all 4 files."""
    (tmp_path / "CivicSurvival" / "Properties").mkdir(parents=True)
    (tmp_path / "CivicSurvival" / "CivicSurvival.csproj").write_text(
        CSPROJ_TEMPLATE.format(version="0.3.25"), encoding="utf-8"
    )
    (tmp_path / "CivicSurvival" / "manifest.json").write_text(
        MANIFEST_TEMPLATE.format(version="0.3.25"), encoding="utf-8"
    )
    (tmp_path / "CivicSurvival" / "Properties" / "PublishConfiguration.xml").write_text(
        XML_TEMPLATE.format(version="0.3.25", summary="Initial release."),
        encoding="utf-8",
    )
    (tmp_path / "CivicSurvival" / "Properties" / "CHANGELOG.md").write_text(
        CHANGELOG_TEMPLATE.format(version="0.3.25"), encoding="utf-8"
    )

    script = ROOT / "scripts" / "release.py"

    # verify: should pass.
    verify = subprocess.run(
        [sys.executable, str(script), "--repo", str(tmp_path), "verify"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert verify.returncode == 0, verify.stderr

    # bump: should succeed and report the new version.
    bump = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo",
            str(tmp_path),
            "bump",
            "--version",
            "0.3.26",
            "--title",
            "End-to-end test release",
            "--summary",
            "End-to-end test release.",
            "--bullet",
            "Atomic across four files.",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bump.returncode == 0, bump.stderr
    assert "0.3.25 -> 0.3.26" in bump.stdout

    # current: should print the new version.
    current = subprocess.run(
        [sys.executable, str(script), "--repo", str(tmp_path), "current"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert current.returncode == 0
    assert current.stdout.strip() == "0.3.26"
