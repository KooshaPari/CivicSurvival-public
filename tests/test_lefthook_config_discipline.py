"""Tests for the lefthook pre-push gate config.

Validates that the developer-side pre-push gates mirror what CI runs.
A contributor who deletes or breaks .lefthook.yml would lose the
"fail-fast locally before pushing" guarantee -- this test catches it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
LEFTHOOK = ROOT / ".lefthook.yml"


def test_lefthook_yaml_exists():
    assert LEFTHOOK.exists(), f"missing {LEFTHOOK.name} -- developer pre-push gate"
    assert LEFTHOOK.stat().st_size > 200, "lefthook.yml looks too small to be real"


def test_lefthook_yaml_is_parseable():
    # Should never raise.
    cfg = yaml.safe_load(LEFTHOOK.read_text(encoding="utf-8"))
    assert isinstance(cfg, dict)
    assert cfg.get("min_version"), "min_version required by lefthook schema"


def test_lefthook_has_pre_commit_and_pre_push():
    cfg = yaml.safe_load(LEFTHOOK.read_text(encoding="utf-8"))
    assert "pre-commit" in cfg, "pre-commit hook required"
    assert "pre-push" in cfg, "pre-push hook required"


def test_pre_commit_includes_ruff_prettier_gitleaks():
    cfg = yaml.safe_load(LEFTHOOK.read_text(encoding="utf-8"))
    names = list(cfg["pre-commit"].get("commands", {}).keys())
    assert "ruff_format_check" in names
    assert "ruff_lint" in names
    assert "prettier_check" in names
    assert "gitleaks_protect" in names, "gitleaks pre-commit gate required for secret safety"


def test_pre_push_includes_pytest_scorecard_release_verify():
    cfg = yaml.safe_load(LEFTHOOK.read_text(encoding="utf-8"))
    names = list(cfg["pre-push"].get("commands", {}).keys())
    assert "pytest_discipline" in names
    assert "scorecard_regression_check" in names
    assert "release_atomicity" in names, "release verify required pre-push"
    assert "gitleaks_full_diff" in names, "full-diff gitleaks required pre-push"


def test_pre_push_gitleaks_uses_local_config():
    """The pre-push gitleaks call must reference .gitleaks.toml allowlist."""
    text = LEFTHOOK.read_text(encoding="utf-8")
    assert "--config .gitleaks.toml" in text, "must reference repo-local gitleaks config"


def test_pre_push_gitleaks_scans_full_repo_not_staged():
    """Pre-push gitleaks must scan the full git source, not just staged files."""
    text = LEFTHOOK.read_text(encoding="utf-8")
    # Look in the post-merge/pre-push blocks for the gitleaks command that
    # scans full source (not --staged).
    pre_push_section = text[text.index("pre-push:"):]
    # Find the gitleaks_full_diff block (full source scan, not staged).
    block = pre_push_section[pre_push_section.index("gitleaks_full_diff"):]
    assert "--source ." in block, (
        "must use --source . to scan full git history (not --staged)"
    )
    assert "gitleaks detect" in block, "must call `gitleaks detect` for full-history scan"
    assert "--staged" not in block, "pre-push should NOT use --staged (that's pre-commit)"
    assert "--no-banner" in block, "must pass --no-banner for CI-friendly output"


def test_lefthook_does_not_run_powershell():
    """No PowerShell -- the project ships compiled native bins."""
    text = LEFTHOOK.read_text(encoding="utf-8")
    # Allow ps1 paths in comments but never as actual commands.
    ps1_in_run = re.search(r"^\s*run:\s+.*\.ps1", text, re.MULTILINE)
    assert ps1_in_run is None, f"PowerShell in lefthook command: {ps1_in_run.group(0)}"


def test_lefthook_uses_uv_for_python():
    """uv is the canonical Python runner in this repo."""
    text = LEFTHOOK.read_text(encoding="utf-8")
    assert "uv run pytest" in text, "must use `uv run` for pytest (matches CI)"


def test_install_instructions_exist_in_readme():
    """README must document how to install lefthook so contributors can run the gates."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="ignore")
    assert "lefthook" in readme.lower(), "README must mention lefthook install"


def test_gitleaks_config_exists():
    """lefthook references .gitleaks.toml -- it must exist."""
    assert (ROOT / ".gitleaks.toml").exists(), "lefthook gates depend on .gitleaks.toml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
