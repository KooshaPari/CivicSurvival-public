import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "public-audit.yml"


def _workflow() -> dict:
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
        input=WORKFLOW.read_text(),
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(result.stdout)


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
    job = workflow["jobs"]["public-audit"]

    assert workflow["permissions"] == {"contents": "read"}
    assert "env" not in workflow
    assert "env" not in job
    assert all("env" not in step for step in job["steps"])
    assert "secrets." not in WORKFLOW.read_text()
