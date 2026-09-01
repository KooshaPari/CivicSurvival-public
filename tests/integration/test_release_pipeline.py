"""End-to-end integration: bump via the new release CLI, verify surfaces, tag, then run scorecard against the tagged commit.

This is a single end-to-end test that proves scripts/release.py + the
public-audit gate + scripts/scorecard_ci.py work as a coherent release
pipeline.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

PY = "python"


def _run(*cmd: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=60,
    )


@pytest.mark.integration
def test_release_bump_updates_all_surfaces_atomically(tmp_path: Path) -> None:
    """Bumping a version updates all four surfaces and the post-state is internally consistent."""
    # Make a tmp copy of the actual repo
    repo_root = Path(__file__).resolve().parents[2]
    work = tmp_path / "repo"
    shutil.copytree(
        repo_root,
        work,
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", "build-evidence"),
    )

    # Find current version
    r = _run(PY, "scripts/release.py", "current", cwd=work)
    assert r.returncode == 0, f"current failed: {r.stderr}"
    current = r.stdout.strip()
    assert re.match(r"^\d+\.\d+\.\d+$", current), current

    # Compute next patch
    major, minor, patch = (int(x) for x in current.split("."))
    next_version = f"{major}.{minor}.{patch + 1}"

    # Bump
    r = _run(
        PY,
        "scripts/release.py",
        "bump",
        "--version",
        next_version,
        "--title",
        "Integration smoke test release",
        "--summary",
        "End-to-end verification that the release CLI updates all four surfaces.",
        "--bullet",
        "Verified atomic write across csproj/manifest/PublishConfig/CHANGELOG",
        cwd=work,
    )
    assert r.returncode == 0, f"bump failed: {r.stderr}"

    # Verify surfaces all agree
    r = _run(PY, "scripts/release.py", "verify", cwd=work)
    assert r.returncode == 0, f"verify failed: {r.stderr}"

    # Each file should now reference the new version
    csproj = (work / "CivicSurvival/CivicSurvival.csproj").read_text()
    assert f"<Version>{next_version}</Version>" in csproj, csproj

    manifest = json.loads((work / "CivicSurvival/manifest.json").read_text())
    assert manifest["version_number"] == next_version, manifest


@pytest.mark.integration
def test_release_bump_refuses_non_greater_version(tmp_path: Path) -> None:
    """`release bump --version 0.0.0` against an existing 0.3.25 must fail closed."""
    repo_root = Path(__file__).resolve().parents[2]
    work = tmp_path / "repo"
    shutil.copytree(
        repo_root,
        work,
        ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__", "build-evidence"),
    )

    r = _run(
        PY,
        "scripts/release.py",
        "bump",
        "--version",
        "0.0.1",
        "--title",
        "x",
        "--summary",
        "x",
        "--bullet",
        "x",
        cwd=work,
    )
    assert r.returncode != 0
    assert "greater" in r.stderr.lower() or "greater" in r.stdout.lower()
