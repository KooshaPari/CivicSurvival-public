"""Tests for the self-hosted runner hardening contract.

GitHub's self-hosted runners are the single biggest attack surface for
an OSS repo: the runner VM has full network access, the persistent
self-hosted devbox (G:/ here) holds the closed CS2 Modding Toolkit,
and any compromised action step can exfiltrate either.

These tests enforce the hardening pattern from GitHub's "Hardening
guides for self-hosted runners":
  - ephemeral runner label (no persistent VM reuse)
  - persist-credentials: false on checkout (no GITHUB_TOKEN to next step)
  - per-job minimal permissions block (no global write)
  - actions pinned by SHA, not by tag
  - concurrency group on the release pipeline (no two releases racing)
  - audit step that captures runner identity
  - retention-days on every artifact
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
RELEASE_YML = ROOT / ".github" / "workflows" / "release.yml"


def _load() -> dict:
    return yaml.safe_load(RELEASE_YML.read_text(encoding="utf-8"))


def test_release_yml_exists_and_is_parseable():
    assert RELEASE_YML.exists(), "release.yml missing"
    cfg = _load()
    assert cfg.get("name") == "release"


def test_release_yml_has_concurrency_block():
    """Prevents two parallel releases from racing on the same tag."""
    cfg = _load()
    assert "concurrency" in cfg, "concurrency block required to prevent race"
    assert "group" in cfg["concurrency"]
    assert "release-" in cfg["concurrency"]["group"]


def test_self_hosted_job_requires_ephemeral_label():
    """The persistent G:/ devbox MUST NOT be a release runner."""
    cfg = _load()
    build = cfg["jobs"]["build"]
    runs_on = build["runs-on"]
    assert isinstance(runs_on, list), "runs-on must be a list (label matrix)"
    assert "self-hosted" in runs_on
    assert "ephemeral" in runs_on, (
        "build job must require 'ephemeral' label so the runner is "
        "a fresh VM per job, not the persistent G:/ devbox"
    )


def test_self_hosted_job_has_timeout():
    """Hard upper bound on runner lifetime -- prevents runaway processes."""
    cfg = _load()
    assert "timeout-minutes" in cfg["jobs"]["build"], (
        "self-hosted build must have timeout-minutes"
    )
    assert cfg["jobs"]["build"]["timeout-minutes"] <= 60


def test_self_hosted_job_does_not_have_global_write():
    """Per-job permissions block scopes write to what's actually needed."""
    cfg = _load()
    build = cfg["jobs"]["build"]
    assert "permissions" in build, "self-hosted job must declare its own permissions"
    perms = build["permissions"]
    # contents is read (not write) -- assembly job owns the release artifact.
    assert perms.get("contents") == "read", (
        "self-hosted job must NOT have contents:write -- it only builds"
    )
    assert "actions" in perms, "actions permission must be explicitly scoped"


def test_checkout_uses_persist_credentials_false():
    """Critical: prevents GITHUB_TOKEN leakage to subsequent steps."""
    cfg = _load()
    text = RELEASE_YML.read_text(encoding="utf-8")
    # Every checkout action in the file must set persist-credentials: false.
    for job_name, job in cfg["jobs"].items():
        for step in job.get("steps", []):
            uses = step.get("uses", "")
            if uses.startswith("actions/checkout"):
                # Find the matching with: block
                idx = text.index(f"- uses: {uses.split('@')[0]}")
                with_block = text[idx:idx + 600]
                assert "persist-credentials: false" in with_block, (
                    f"job {job_name} checkout must set persist-credentials: false"
                )


def test_actions_pinned_by_sha_not_by_tag():
    """Every actions/* ref must be a 40-char SHA, not a tag like @v4."""
    cfg = _load()
    # Find any uses: line; the SHA is the substring after @ up to the first
    # whitespace/comment/eol. Allow 40-char SHA only.
    pattern = re.compile(r"uses:\s+([\w./\-]+)@([0-9a-f]{40})(?:$|\s|#|/)", re.MULTILINE)
    tag_pattern = re.compile(r"uses:\s+[\w./\-]+@v\d", re.IGNORECASE)
    text = RELEASE_YML.read_text(encoding="utf-8")

    # First, fail fast if any uses: line has a tag-style @vN ref at all.
    tag_hit = tag_pattern.search(text)
    assert not tag_hit, (
        f"release.yml has a tag-pinned action: {tag_hit.group(0)!r}; "
        f"all actions must be SHA-pinned (40-char hex)"
    )

    # When YAML loads, uses becomes just the string after `uses:`, e.g.
    # "actions/checkout@6929ba2dd83ce7609a7fc3a72e4da9dd2e61319f" — no
    # leading `uses:` prefix. The regex matches the action name and the
    # trailing 40-char SHA only.
    pattern = re.compile(r"^([\w./\-]+)@([0-9a-f]{40})$")
    pinned = []
    for job_name, job in cfg["jobs"].items():
        for step in job.get("steps", []):
            uses = step.get("uses", "")
            if not uses:
                continue
            m = pattern.match(uses)
            assert m, (
                f"job {job_name} step {step.get('name', '?')!r} uses "
                f"action {uses!r} without SHA pin (must be 40-char SHA, not @v4)"
            )
            pinned.append((job_name, step.get("name"), m.group(1), m.group(2)[:8]))
    assert pinned, "expected at least one action pinned by SHA"


def test_release_yml_has_audit_step_on_self_hosted():
    """Self-hosted runner must log who it is and what sha it's building."""
    cfg = _load()
    steps = cfg["jobs"]["build"]["steps"]
    audit_steps = [
        s for s in steps
        if s.get("name", "").lower().startswith("audit")
        or "runner" in s.get("run", "").lower()
    ]
    assert audit_steps, (
        "self-hosted job must have an audit step that captures "
        "runner identity + ACTIONS_STEP_DEBUG + sha"
    )


def test_artifacts_have_retention_days():
    """Artifact retention is a security control -- too long == evidence lingers."""
    cfg = _load()
    for job_name, job in cfg["jobs"].items():
        for step in job.get("steps", []):
            uses = step.get("uses", "")
            if not uses.startswith("actions/upload-artifact"):
                continue
            with_block = step.get("with", {})
            assert "retention-days" in with_block, (
                f"job {job_name} upload-artifact must set retention-days"
            )
            assert with_block["retention-days"] <= 90, (
                f"job {job_name} retention-days too long: "
                f"{with_block['retention-days']} > 90"
            )


def test_release_yml_does_not_use_powershell_for_release():
    """The release pipeline must be PowerShell-free (compiled native bins only)."""
    text = RELEASE_YML.read_text(encoding="utf-8")
    # PowerShell is allowed in comment lines only.
    non_comment_lines = [
        line for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    non_comment = "\n".join(non_comment_lines)
    assert "pwsh" not in non_comment, "release.yml must not invoke PowerShell"
    assert "powershell:" not in non_comment, "release.yml must not declare shell: powershell"


def test_assemble_job_pins_oidc_off():
    """assemble job must explicitly disable OIDC token issuance."""
    cfg = _load()
    assemble = cfg["jobs"]["assemble"]
    assert "permissions" in assemble
    assert assemble["permissions"].get("id-token") == "none", (
        "assemble job must set id-token: none to prevent OIDC token issuance"
    )
