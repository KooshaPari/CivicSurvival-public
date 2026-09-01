"""Tests for scripts/ci/check-public-audit.mjs — version drift and policy checks.

Runs the script via bun against an ephemeral copy of the repo with targeted
mutations to assert that each failure path triggers correctly.

Skipped when neither bun nor node is on PATH.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "ci" / "check-public-audit.mjs"


def _resolve_runtime() -> str | None:
    """Locate a JS runtime. Falls back to the known user-local bun install."""
    for name in ("bun", "node", "nodejs"):
        found = shutil.which(name)
        if found:
            return found
    bun = Path.home() / ".bun" / "bin" / ("bun.exe" if Path.home().drive else "bun")
    return str(bun) if bun.exists() else None


RUNTIME = _resolve_runtime()
pytestmark = pytest.mark.skipif(not RUNTIME, reason="node/bun runtime required")


def _runtime() -> list[str]:
    return [RUNTIME] if RUNTIME == shutil.which("bun") else [RUNTIME]


def _seed(tmp_path: Path) -> None:
    """Copy the repo skeleton the script needs to run, into tmp_path."""
    shutil.copytree(ROOT / "CivicSurvival", tmp_path / "CivicSurvival")
    shutil.copy(ROOT / "PRIVACY.md", tmp_path / "PRIVACY.md")
    shutil.copy(ROOT / "LICENSE", tmp_path / "LICENSE")
    shutil.copy(ROOT / "NOTICE.md", tmp_path / "NOTICE.md")
    (tmp_path / "Assets").mkdir()
    shutil.copy(ROOT / "Assets" / "LICENSE", tmp_path / "Assets" / "LICENSE")
    shutil.copy(ROOT / "Assets" / "README.md", tmp_path / "Assets" / "README.md")
    shutil.copytree(
        ROOT / "scripts" / "ci",
        tmp_path / "scripts" / "ci",
    )


def _run(tmp_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [*_runtime(), str(SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )


def _mutate(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"marker not found in {path}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def test_clean_repo_state_passes(tmp_path):
    _seed(tmp_path)
    proc = _run(tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"
    assert payload["version"] == "0.3.25"


def test_drift_between_csproj_and_manifest_fails(tmp_path):
    _seed(tmp_path)
    manifest = tmp_path / "CivicSurvival" / "manifest.json"
    _mutate(manifest, '"version_number": "0.3.25"', '"version_number": "9.9.9"')
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "manifest=9.9.9" in proc.stderr


def test_drift_between_csproj_and_publishconfig_fails(tmp_path):
    _seed(tmp_path)
    xml = tmp_path / "CivicSurvival" / "Properties" / "PublishConfiguration.xml"
    _mutate(xml, '<ModVersion Value="0.3.25" />', '<ModVersion Value="9.9.9" />')
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "publishConfig=9.9.9" in proc.stderr


def test_drift_between_manifest_and_publishconfig_while_csproj_matches_neither_fails(
    tmp_path,
):
    """A future contributor bumps csproj+manifest to 0.3.26 but forgets PublishConfig.

    This is the exact drift class that bit PR #46/#47.
    """
    _seed(tmp_path)
    csproj = tmp_path / "CivicSurvival" / "CivicSurvival.csproj"
    manifest = tmp_path / "CivicSurvival" / "manifest.json"
    _mutate(csproj, "<Version>0.3.25</Version>", "<Version>0.3.26</Version>")
    _mutate(manifest, '"version_number": "0.3.25"', '"version_number": "0.3.26"')
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "publishConfig=0.3.25" in proc.stderr
    assert "project=0.3.26" in proc.stderr


def test_publishconfig_format_is_strictly_enforced(tmp_path):
    """Whitespace or attribute reordering is rejected so we catch any drift.

    The build tooling always emits canonical single-space formatting; if a
    future hand-edit introduces relaxed formatting, the script fails closed
    rather than silently accepting the new shape.
    """
    _seed(tmp_path)
    xml = tmp_path / "CivicSurvival" / "Properties" / "PublishConfiguration.xml"
    _mutate(xml, '<ModVersion Value="0.3.25" />', '<ModVersion  Value = "0.3.25" />')
    proc = _run(tmp_path)
    assert proc.returncode != 0
    assert "publishConfig=undefined" in proc.stderr
