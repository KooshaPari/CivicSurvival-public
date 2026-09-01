import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
GENERATOR = ROOT / "Tools" / "generate-binding-manifest.js"
SYNC = ROOT / "Tools" / "sync-binding-codegen.js"
CONTRACT_CHECK = ROOT / "scripts" / "contract_check.py"


def projection_fixture(tmp_path: Path) -> Path:
    for relative in (
        "CivicSurvival.sln",
        "CivicSurvival.Contracts/CivicSurvival.Contracts.csproj",
        "CivicSurvival/Core/UI/BindingNames.cs",
        "CivicSurvival/Core/UI/BindingNames.Dto.g.cs",
        "CivicSurvival/Core/UI/BindingNames.Trigger.g.cs",
        "CivicSurvival/UI/src/hooks/bindingNames.generated.ts",
        "CivicSurvival/UI/src/hooks/typedBinding.generated.ts",
        "CivicSurvival/UI/src/types/triggerSignatures.generated.ts",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return tmp_path


def run(script: Path, root: Path):
    env = os.environ | {"CIVIC_REPO_ROOT": str(root)}
    return subprocess.run(
        ["node", str(script), "--check"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def run_contract_check(root: Path):
    env = os.environ | {"CIVIC_REPO_ROOT": str(root)}
    return subprocess.run(
        ["python3", str(CONTRACT_CHECK)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def test_binding_manifest_rejects_stale_or_generated_only_values(tmp_path):
    root = projection_fixture(tmp_path)
    generated = root / "CivicSurvival/UI/src/hooks/bindingNames.generated.ts"
    text = generated.read_text()
    generated.write_text(
        text.replace('    Group: "CivicSurvival",\n', "", 1) + '    StaleOnly: "StaleOnly",\n'
    )

    result = run(GENERATOR, root)

    assert result.returncode != 0
    assert "binding manifest check failed" in result.stderr


def test_binding_manifest_rejects_member_rename_with_same_value(tmp_path):
    root = projection_fixture(tmp_path)
    generated = root / "CivicSurvival/UI/src/hooks/bindingNames.generated.ts"
    generated.write_text(
        generated.read_text().replace(
            '    Group: "CivicSurvival",', '    RenamedGroup: "CivicSurvival",', 1
        )
    )

    result = run(GENERATOR, root)

    assert result.returncode != 0
    assert "binding manifest check failed" in result.stderr

    contract_result = run_contract_check(root)

    assert contract_result.returncode != 0
    assert "binding projection mismatch" in contract_result.stderr


def test_codegen_rejects_empty_projection(tmp_path):
    root = projection_fixture(tmp_path)
    (root / "CivicSurvival/UI/src/hooks/typedBinding.generated.ts").write_text("")

    result = run(SYNC, root)

    assert result.returncode != 0
    assert "empty" in result.stderr
