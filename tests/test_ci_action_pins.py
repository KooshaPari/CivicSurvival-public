import re
from pathlib import Path

CI_WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "ci.yml"
ACTION_KEY = re.compile(r"^\s*(?:-\s*)?uses:")
IMMUTABLE_ACTION = re.compile(r"^\s*(?:-\s*)?uses:\s+[^\s@]+@[0-9a-f]{40}\s+#\s+\S.*$")


def test_ci_actions_use_immutable_commits_with_provenance_comments():
    action_lines = [
        line for line in CI_WORKFLOW.read_text().splitlines() if ACTION_KEY.match(line)
    ]

    assert action_lines, "CI workflow must invoke at least one external action"
    assert all(IMMUTABLE_ACTION.match(line) for line in action_lines), action_lines


def test_ci_runs_action_pin_policy_in_hosted_python_job():
    test_path = "tests/test_ci_action_pins.py"
    run_lines = [
        line.strip()
        for line in CI_WORKFLOW.read_text().splitlines()
        if line.strip().startswith("run:")
    ]

    for command in ("ruff check", "ruff format --check", "python3 -m pytest"):
        assert any(
            line.startswith(f"run: {command}") and test_path in line
            for line in run_lines
        )
