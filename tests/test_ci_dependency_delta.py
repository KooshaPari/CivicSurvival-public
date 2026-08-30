from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "dependency_delta.py"


def load_module():
    spec = importlib.util.spec_from_file_location("dependency_delta", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_package_lock_change_runs_the_locked_node_audit(tmp_path):
    module = load_module()
    ui = tmp_path / "CivicSurvival" / "UI"
    ui.mkdir(parents=True)
    (ui / "package.json").write_text('{"name":"civic-ui"}')
    (ui / "package-lock.json").write_text('{"lockfileVersion":3}')

    plan = module.build_scan_plan(tmp_path, ["CivicSurvival/UI/package-lock.json"])

    assert [(item.ecosystem, item.cwd, item.command) for item in plan] == [
        (
            "node",
            ui,
            ("npm", "audit", "--package-lock-only", "--audit-level=low", "--omit=dev"),
        )
    ]


def test_csharp_lockfile_change_runs_locked_restore_then_vulnerability_scan(tmp_path):
    module = load_module()
    solution = tmp_path / "CivicSurvival.sln"
    solution.write_text("Microsoft Visual Studio Solution File")
    project = tmp_path / "CivicSurvival.Contracts"
    project.mkdir()
    (project / "packages.lock.json").write_text("{}")

    plan = module.build_scan_plan(tmp_path, ["CivicSurvival.Contracts/packages.lock.json"])

    assert [(item.ecosystem, item.cwd, item.command) for item in plan] == [
        ("csharp", tmp_path, ("dotnet", "restore", "CivicSurvival.sln", "--locked-mode")),
        (
            "csharp",
            tmp_path,
            ("dotnet", "list", "CivicSurvival.sln", "package", "--vulnerable", "--include-transitive"),
        ),
    ]


def test_node_manifest_without_lockfile_fails_with_path_ecosystem_and_remedy(tmp_path):
    module = load_module()
    ui = tmp_path / "CivicSurvival" / "UI"
    ui.mkdir(parents=True)
    (ui / "package.json").write_text('{"name":"civic-ui"}')

    with pytest.raises(module.DependencyDeltaError) as excinfo:
        module.build_scan_plan(tmp_path, ["CivicSurvival/UI/package.json"])

    message = str(excinfo.value)
    assert "CivicSurvival/UI/package.json" in message
    assert "node" in message
    assert "package-lock.json" in message


def test_unsupported_manifest_fails_with_path_ecosystem_and_remedy(tmp_path):
    module = load_module()
    native = tmp_path / "native"
    native.mkdir()
    (native / "Cargo.toml").write_text("[package]\nname = 'civic'\n")

    with pytest.raises(module.DependencyDeltaError) as excinfo:
        module.build_scan_plan(tmp_path, ["native/Cargo.toml"])

    message = str(excinfo.value)
    assert "native/Cargo.toml" in message
    assert "rust" in message
    assert "scanner" in message


def test_csharp_project_without_lockfile_fails_with_path_ecosystem_and_remedy(tmp_path):
    module = load_module()
    (tmp_path / "CivicSurvival.sln").write_text("Microsoft Visual Studio Solution File")
    project = tmp_path / "CivicSurvival.Contracts"
    project.mkdir()
    (project / "CivicSurvival.Contracts.csproj").write_text("<Project />")

    with pytest.raises(module.DependencyDeltaError) as excinfo:
        module.build_scan_plan(tmp_path, ["CivicSurvival.Contracts/CivicSurvival.Contracts.csproj"])

    message = str(excinfo.value)
    assert "CivicSurvival.Contracts/CivicSurvival.Contracts.csproj" in message
    assert "csharp" in message
    assert "packages.lock.json" in message


def test_scanner_failure_propagates_to_the_required_gate(tmp_path):
    module = load_module()
    ui = tmp_path / "CivicSurvival" / "UI"
    ui.mkdir(parents=True)
    command = module.ScanCommand(
        ecosystem="node",
        cwd=ui,
        command=("npm", "audit", "--package-lock-only", "--audit-level=low", "--omit=dev"),
    )

    def failing_runner(*_args, **_kwargs):
        return type("Result", (), {"returncode": 1})()

    with pytest.raises(module.DependencyDeltaError, match="node scanner failed"):
        module.run_scan_plan([command], runner=failing_runner)


def test_ci_aggregate_gates_reject_failed_or_skipped_required_results():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    security_job = workflow.split("  security:\n", 1)[1].split("\n  dep-review:\n", 1)[0]
    dependency_job = workflow.split("  dep-review:\n", 1)[1].split("\n  civic-quality:\n", 1)[0]

    assert "continue-on-error" not in security_job
    assert "continue-on-error" not in dependency_job
    assert "actions/dependency-review-action" not in dependency_job
    assert "python3 scripts/dependency_delta.py" in dependency_job
    assert 'if [ "$name" = "security" ]; then' in workflow
    assert 'if [ "$event_name" = "pull_request" ] && [ "$name" = "dep-review" ]; then' in workflow
    assert 'if [ "$required" -eq 1 ] && [ "$result" != "success" ]; then' in workflow
    assert 'lint_result="${{ needs.lint.result }}"' in workflow
    assert 'if [ "$lint_result" != "success" ]; then' in workflow
