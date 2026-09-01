from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "civic_quality_gate.py"


def write_policy(root: Path, rules: list[dict], required: list[str] | None = None) -> Path:
    path = root / "policy.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "required_rule_ids": required or [rule["id"] for rule in rules],
                "rules": rules,
            }
        )
    )
    return path


def run_gate(root: Path, policy: Path, output: str = "json", strict: bool = True):
    command = [sys.executable, str(SCRIPT), str(root), "--policy", str(policy), "--output", output]
    if strict:
        command.append("--strict")
    return subprocess.run(command, text=True, capture_output=True)


def test_complete_file_and_text_policy_passes(tmp_path):
    (tmp_path / "README.md").write_text("public snapshot; see BUILDING.md")
    (tmp_path / "BUILDING.md").write_text("host required")
    policy = write_policy(
        tmp_path,
        [
            {
                "id": "CIVIC-DOC-001",
                "kind": "all_paths_exist",
                "paths": ["README.md", "BUILDING.md"],
            },
            {
                "id": "CIVIC-DOC-002",
                "kind": "text_contains",
                "path": "README.md",
                "contains": ["public snapshot", "BUILDING.md"],
            },
        ],
    )
    result = run_gate(tmp_path, policy)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["required_passed"] is True
    assert report["passed_rule_ids"] == ["CIVIC-DOC-001", "CIVIC-DOC-002"]


def test_missing_required_evidence_is_actionable(tmp_path):
    policy = write_policy(
        tmp_path,
        [{"id": "CIVIC-DOC-001", "kind": "all_paths_exist", "paths": ["README.md"]}],
    )
    result = run_gate(tmp_path, policy)
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["required_passed"] is False
    assert [failure["id"] for failure in report["failed_rules"]] == ["CIVIC-DOC-001"]


@pytest.mark.parametrize(
    "policy_data",
    [
        {
            "version": 1,
            "required_rule_ids": ["A", "A"],
            "rules": [{"id": "A", "kind": "all_paths_exist", "paths": []}],
        },
        {
            "version": 1,
            "required_rule_ids": ["A"],
            "rules": [{"id": "A", "kind": "unknown", "paths": []}],
        },
        {"version": 1, "required_rule_ids": [], "rules": []},
        {
            "version": 1,
            "required_rule_ids": ["A"],
            "rules": [{"id": "A", "kind": "all_paths_exist", "paths": [7]}],
        },
    ],
)
def test_malformed_policy_exits_two(tmp_path, policy_data):
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps(policy_data))
    result = run_gate(tmp_path, policy)
    assert result.returncode == 2


def test_external_wp01_pending_does_not_fail_strict_gate(tmp_path):
    policy = write_policy(
        tmp_path,
        [{"id": "CIVIC-PROGRAM-002", "kind": "external_gate", "state": "pending"}],
    )
    result = run_gate(tmp_path, policy)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["external_gates"] == [{"external": True, "id": "WP01", "state": "pending"}]


def test_markdown_output_is_stable(tmp_path):
    (tmp_path / "README.md").write_text("ok")
    policy = write_policy(
        tmp_path,
        [{"id": "A", "kind": "all_paths_exist", "paths": ["README.md"]}],
    )
    result = run_gate(tmp_path, policy, output="markdown")
    assert result.returncode == 0
    assert "| Rule | Status |" in result.stdout
    assert "| A | PASS |" in result.stdout
