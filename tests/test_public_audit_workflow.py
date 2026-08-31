import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "public-audit.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SECRET_CONTEXT = re.compile(r"\bsecrets\s*(?:\.|\[)")


def _workflow(path: Path = WORKFLOW) -> dict:
    ruby = shutil.which("ruby")
    assert ruby, "Ruby is required for dependency-free structural YAML validation"
    script = """
require "json"
require "yaml"
source = STDIN.read.sub(/^on:/, '"on":')
puts JSON.generate(YAML.safe_load(source, aliases: true))
"""
    result = subprocess.run(
        [ruby, "-e", script],
        input=path.read_text(),
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(result.stdout)


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _strings(key)
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def _assert_no_secret_or_environment_surface(workflow: dict) -> None:
    job = workflow["jobs"]["public-audit"]

    assert workflow["permissions"] == {"contents": "read"}
    assert "env" not in workflow
    assert "env" not in job
    assert all("env" not in step for step in job["steps"])
    assert all(not SECRET_CONTEXT.search(value) for value in _strings(workflow))


def test_public_audit_cache_supports_both_npm_lockfiles():
    workflow = _workflow()
    steps = workflow["jobs"]["public-audit"]["steps"]
    setup_node = next(
        step for step in steps if "actions/setup-node@" in step.get("uses", "")
    )

    assert setup_node["with"]["cache"] == "npm"
    assert setup_node["with"]["cache-dependency-path"].splitlines() == [
        "CivicSurvival/UI/npm-shrinkwrap.json",
        "CivicSurvival/UI/package-lock.json",
    ]


def test_public_audit_cache_change_has_no_secret_or_environment_surface():
    workflow = _workflow()

    _assert_no_secret_or_environment_surface(workflow)


@pytest.mark.parametrize(
    "expression", ["${{ secrets.TOKEN }}", "${{ secrets['TOKEN'] }}"]
)
def test_public_audit_rejects_secret_context_syntax(expression):
    workflow = _workflow()
    workflow["jobs"]["public-audit"]["name"] = expression

    with pytest.raises(AssertionError):
        _assert_no_secret_or_environment_surface(workflow)


def test_hosted_python_job_runs_public_audit_workflow_policy_tests():
    workflow = _workflow(CI_WORKFLOW)
    steps = {
        step["name"]: step
        for step in workflow["jobs"]["python"]["steps"]
        if "name" in step
    }
    test_path = "tests/test_public_audit_workflow.py"

    assert test_path in steps["Ruff check dependency delta"]["run"]
    assert test_path in steps["Ruff format dependency delta"]["run"]
    assert test_path in steps["Run hostile dependency delta fixtures"]["run"]
