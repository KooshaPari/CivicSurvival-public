import json
import re
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
EXPECTED_INSTALL_STATEMENTS = [
    "set -euo pipefail",
    f'version="{INFISICAL_VERSION}"',
    f'checksum="{INFISICAL_LINUX_AMD64_SHA256}"',
    'archive="$RUNNER_TEMP/infisical-cli.tar.gz"',
    'install_dir="$RUNNER_TEMP/infisical-cli"',
    (
        'url="https://github.com/Infisical/cli/releases/download/v${version}/'
        'cli_${version}_linux_amd64.tar.gz"'
    ),
    'mkdir -p "$install_dir/bin"',
    (
        "curl --fail --location --proto '=https' --tlsv1.2 --silent --show-error "
        '"$url" --output "$archive"'
    ),
    ('printf \'%s %s\\n\' "$checksum" "$archive" | sha256sum --check --strict'),
    'tar -xzf "$archive" -C "$install_dir" infisical',
    'install -m 0755 "$install_dir/infisical" "$install_dir/bin/infisical"',
    'echo "$install_dir/bin" >> "$GITHUB_PATH"',
]
PRIVILEGE_ESCALATION = re.compile(
    r"(?im)(?:^|[;&|]\s*)(?:sudo|doas|pkexec|runuser|su|setpriv)\b"
    r"|(?:--user(?:=|\s+)|run-as\s+)(?:root|0)\b"
    r"|\b(?:uid|euid)\s*=\s*0\b"
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


def _named_step(workflow: dict, name: str) -> dict:
    steps = workflow["jobs"]["sync-secrets"]["steps"]
    matches = [step for step in steps if step.get("name") == name]
    assert len(matches) == 1, (
        f"expected exactly one {name!r} step, found {len(matches)}"
    )
    return matches[0]


def _validation_step() -> dict:
    return _named_step(_workflow(), "Validate Infisical environment")


def _install_step(workflow: dict) -> dict:
    return _named_step(workflow, "Install Infisical CLI")


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


def _assert_safe_install(install: dict) -> None:
    assert install["shell"] == "bash"
    assert not PRIVILEGE_ESCALATION.search(install["run"])
    assert _shell_statements(install["run"]) == EXPECTED_INSTALL_STATEMENTS


def test_infisical_runs_only_when_called_or_manually_dispatched():
    triggers = _workflow()["on"]

    assert set(triggers) == {"workflow_call", "workflow_dispatch"}


def test_infisical_install_is_pinned_verified_and_non_root():
    _assert_safe_install(_install_step(_workflow()))


def test_infisical_validation_does_not_enumerate_secret_environment():
    workflow = _workflow()
    job = workflow["jobs"]["sync-secrets"]
    checkout = _named_step(workflow, "Checkout")
    validation = _named_step(workflow, "Validate Infisical environment")

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


def test_infisical_install_rejects_duplicate_named_step():
    workflow = _workflow()
    steps = workflow["jobs"]["sync-secrets"]["steps"]
    install = next(step for step in steps if step["name"] == "Install Infisical CLI")
    steps.append(dict(install))

    with pytest.raises(AssertionError):
        _install_step(workflow)


def test_infisical_install_rejects_checksum_for_a_different_archive():
    install = _install_step(_workflow())
    install["run"] = install["run"].replace(
        '"$checksum" "$archive" | sha256sum --check --strict',
        '"$checksum" "$RUNNER_TEMP/other.tar.gz" | sha256sum --check --strict',
    )

    with pytest.raises(AssertionError):
        _assert_safe_install(install)


@pytest.mark.parametrize(
    "command",
    [
        "sudo install infisical /usr/local/bin/infisical",
        "doas install infisical /usr/local/bin/infisical",
        "runuser -u root -- install infisical /usr/local/bin/infisical",
        "pkexec install infisical /usr/local/bin/infisical",
        "setpriv --reuid=0 install infisical /usr/local/bin/infisical",
    ],
)
def test_infisical_install_rejects_privilege_escalation(command):
    install = _install_step(_workflow())
    install["run"] += f"\n{command}\n"

    with pytest.raises(AssertionError):
        _assert_safe_install(install)
