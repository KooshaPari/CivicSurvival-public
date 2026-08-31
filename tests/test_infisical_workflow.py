import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "infisical.yml"
EXPECTED_ENVIRONMENT = {
    "INFISICAL_TOKEN": "${{ secrets.INFISICAL_TOKEN }}",
    "INFISICAL_PROJECT_ID": (
        "${{ vars.INFISICAL_PROJECT_ID || secrets.INFISICAL_PROJECT_ID || "
        "'8efe392e-56a6-4c3c-89f9-8141183dd7e8' }}"
    ),
    "INFISICAL_ENV": (
        "${{ vars.INFISICAL_ENV || github.ref == 'refs/heads/main' && 'prod' || "
        "github.ref == 'refs/heads/staging' && 'staging' || 'dev' }}"
    ),
}
EXPECTED_VALIDATION_STATEMENTS = [
    'if [ -z "$INFISICAL_TOKEN" ]; then',
    'echo "::error::INFISICAL_TOKEN secret not configured in repo settings"',
    "exit 1",
    "fi",
    'if [ -z "$INFISICAL_PROJECT_ID" ]; then',
    'echo "::error::INFISICAL_PROJECT_ID var or secret not set"',
    "exit 1",
    "fi",
    (
        'infisical run --projectId "$INFISICAL_PROJECT_ID" --env "$INFISICAL_ENV" '
        "--token \"$INFISICAL_TOKEN\" -- bash -c 'true'"
    ),
]
INFISICAL_VERSION = "0.43.128"
INFISICAL_LINUX_AMD64_SHA256 = (
    "a3f460be321ad46fefba99cba883bcc601d0f18b02849d2d30ae9b398a8d99dc"
)


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


def _validation_step() -> dict:
    steps = _workflow()["jobs"]["sync-secrets"]["steps"]
    return next(
        step for step in steps if step["name"] == "Validate Infisical environment"
    )


def _shell_statements(command: str) -> list[str]:
    statements = []
    continued = ""
    for raw_line in command.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith("\\"):
            continued += f"{line[:-1].strip()} "
            continue
        statements.append(" ".join(f"{continued}{line}".split()))
        continued = ""
    assert not continued, "validation command ends with an incomplete continuation"
    return statements


def _assert_safe_validation(validation: dict) -> None:
    assert validation["env"] == EXPECTED_ENVIRONMENT
    assert _shell_statements(validation["run"]) == EXPECTED_VALIDATION_STATEMENTS


def test_infisical_runs_only_when_called_or_manually_dispatched():
    triggers = _workflow()["on"]

    assert set(triggers) == {"workflow_call", "workflow_dispatch"}


def test_infisical_install_is_pinned_verified_and_non_root():
    workflow = _workflow()
    steps = {step["name"]: step for step in workflow["jobs"]["sync-secrets"]["steps"]}
    install = steps["Install Infisical CLI"]["run"]

    assert f'version="{INFISICAL_VERSION}"' in install
    assert f'checksum="{INFISICAL_LINUX_AMD64_SHA256}"' in install
    assert (
        "https://github.com/Infisical/cli/releases/download/v${version}/"
        "cli_${version}_linux_amd64.tar.gz" in install
    )
    assert "sha256sum --check --strict" in install
    assert 'tar -xzf "$archive" -C "$install_dir" infisical' in install
    assert (
        'install -m 0755 "$install_dir/infisical" "$install_dir/bin/infisical"'
        in install
    )
    assert 'echo "$install_dir/bin" >> "$GITHUB_PATH"' in install
    assert "setup.deb.sh" not in install
    assert "apt-get" not in install
    assert "sudo" not in install
    assert "curl |" not in install


def test_infisical_validation_does_not_enumerate_secret_environment():
    workflow = _workflow()
    job = workflow["jobs"]["sync-secrets"]
    steps = {step["name"]: step for step in job["steps"]}
    checkout = steps["Checkout"]
    validation = steps["Validate Infisical environment"]

    assert job["permissions"] == {"contents": "read"}
    assert checkout["with"]["persist-credentials"] is False
    _assert_safe_validation(validation)


@pytest.mark.parametrize("name", EXPECTED_ENVIRONMENT)
def test_infisical_validation_rejects_incorrect_credential_mapping(name):
    validation = _validation_step()
    validation["env"][name] = "incorrect"

    with pytest.raises(AssertionError):
        _assert_safe_validation(validation)


def test_infisical_validation_rejects_appended_secret_output():
    validation = _validation_step()
    validation["run"] += '\necho "$INFISICAL_TOKEN"\n'

    with pytest.raises(AssertionError):
        _assert_safe_validation(validation)
