import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "infisical.yml"


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


def test_infisical_runs_only_when_called_or_manually_dispatched():
    triggers = _workflow()["on"]

    assert set(triggers) == {"workflow_call", "workflow_dispatch"}


def test_infisical_validation_does_not_enumerate_secret_environment():
    workflow = _workflow()
    job = workflow["jobs"]["sync-secrets"]
    steps = {step["name"]: step for step in job["steps"]}
    checkout = steps["Checkout"]
    validation = steps["Validate Infisical environment"]
    command = validation["run"]

    assert job["permissions"] == {"contents": "read"}
    assert checkout["with"]["persist-credentials"] is False
    assert set(validation["env"]) == {
        "INFISICAL_TOKEN",
        "INFISICAL_PROJECT_ID",
        "INFISICAL_ENV",
    }
    assert "infisical run" in command
    assert "-- bash -c 'true'" in command
    assert "infisical secrets" not in command
    assert "printenv" not in command
    assert "\nenv" not in command
