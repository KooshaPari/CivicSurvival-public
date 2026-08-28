import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
VERIFIER = ROOT / "scripts" / "verify_wp01_evidence.py"


def run(repo: Path, manifest: Path):
    return subprocess.run(
        ["python3", str(VERIFIER), str(repo), str(manifest)],
        text=True,
        capture_output=True,
    )


def git_head(repo: Path) -> str:
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "tests@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Civic tests"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "evidence.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "--quiet", "-m", "evidence"], check=True)
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def test_template_is_pending(tmp_path):
    manifest = tmp_path / "evidence.json"
    manifest.write_text((ROOT / ".agileplus/civic-warfare-program/wp01-evidence.template.json").read_text())
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "pending" in result.stdout


def test_accepted_manifest_verifies_hashes_and_host(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("licensed smoke output\n")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    subject_commit = git_head(tmp_path)
    manifest = tmp_path / "evidence.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "civic.wp01.evidence", "schema_version": 1,
                "subject": {"commit": subject_commit},
                "environment": {"host_class": "licensed-game", "license_basis": "record"},
                "artifacts": [{"artifact_id": "out", "path": "evidence.txt", "size_bytes": artifact.stat().st_size, "sha256": digest}],
                "commands": [{"command_id": "run"}],
                "evidence": [{"evidence_id": evidence_id, "status": "pass", "subject_commit": subject_commit, "command_ids": ["run"], "artifact_ids": ["out"]} for evidence_id in sorted({"WP01:public_audit_build", "WP01:baseline_tests", "WP01:licensed_adapter_build", "WP01:launch_smoke", "WP01:artifact_hash_provenance", "WP01:agileplus_evidence_record"})],
                "decision": {"result": "GO"},
            }
        )
    )
    result = run(tmp_path, manifest)
    assert result.returncode == 0
    assert "accepted" in result.stdout


def test_tampered_artifact_is_rejected(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("original\n")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    artifact.write_text("tampered\n")
    subject_commit = git_head(tmp_path)
    manifest = tmp_path / "evidence.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "civic.wp01.evidence", "schema_version": 1,
                "subject": {"commit": subject_commit},
                "environment": {"host_class": "licensed-game", "license_basis": "record"},
                "artifacts": [{"artifact_id": "out", "path": "evidence.txt", "size_bytes": artifact.stat().st_size, "sha256": digest}],
                "commands": [{"command_id": "run"}],
                "evidence": [{"evidence_id": evidence_id, "status": "pass", "subject_commit": subject_commit, "command_ids": ["run"], "artifact_ids": ["out"]} for evidence_id in sorted({"WP01:public_audit_build", "WP01:baseline_tests", "WP01:licensed_adapter_build", "WP01:launch_smoke", "WP01:artifact_hash_provenance", "WP01:agileplus_evidence_record"})],
                "decision": {"result": "GO"},
            }
        )
    )
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "sha256 mismatch" in result.stderr


def test_non_object_manifest_fields_fail_closed(tmp_path):
    manifest = tmp_path / "evidence.json"
    manifest.write_text(json.dumps([]))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "top level must be an object" in result.stderr

    manifest.write_text(json.dumps({"schema": "civic.wp01.evidence", "schema_version": 1, "decision": []}))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "decision must be an object" in result.stderr


def test_subject_commit_must_match_checkout(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("licensed smoke output\n")
    subject_commit = git_head(tmp_path)
    manifest = tmp_path / "evidence.json"
    manifest.write_text(json.dumps({"schema": "civic.wp01.evidence", "schema_version": 1, "subject": {"commit": "a" * 40}, "decision": {"result": "GO"}}))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert subject_commit in result.stderr


def test_malformed_command_and_evidence_entries_fail_closed(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("x\n")
    subject_commit = git_head(tmp_path)
    manifest = tmp_path / "evidence.json"
    common = {"schema": "civic.wp01.evidence", "schema_version": 1, "subject": {"commit": subject_commit}, "environment": {"host_class": "licensed-game", "license_basis": "test"}, "artifacts": [{"artifact_id": "out", "path": "evidence.txt", "size_bytes": artifact.stat().st_size, "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}], "decision": {"result": "GO"}}
    manifest.write_text(json.dumps({**common, "commands": ["run"]}))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "commands must be a list of objects" in result.stderr

    manifest.write_text(json.dumps({**common, "commands": [], "evidence": ["bad"]}))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "evidence must be a list of objects" in result.stderr


def test_duplicate_json_keys_are_rejected(tmp_path):
    manifest = tmp_path / "evidence.json"
    manifest.write_text('{"schema":"civic.wp01.evidence","schema":"civic.wp01.evidence","schema_version":1}')
    result = run(tmp_path, manifest)
    assert result.returncode == 2
    assert "duplicate JSON key" in result.stderr


def test_non_string_ids_fail_closed(tmp_path):
    artifact = tmp_path / "evidence.txt"
    artifact.write_text("x\n")
    subject_commit = git_head(tmp_path)
    manifest = tmp_path / "evidence.json"
    base = {"schema": "civic.wp01.evidence", "schema_version": 1, "subject": {"commit": subject_commit}, "environment": {"host_class": "licensed-game", "license_basis": "test"}, "artifacts": [{"artifact_id": "out", "path": "evidence.txt", "size_bytes": artifact.stat().st_size, "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}], "decision": {"result": "GO"}}
    manifest.write_text(json.dumps({**base, "commands": [{"command_id": []}]}))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "non-empty string command_id" in result.stderr

    valid_evidence = [
        {
            "evidence_id": evidence_id,
            "status": "pass",
            "subject_commit": subject_commit,
            "command_ids": ["run"],
            "artifact_ids": ["out"],
        }
        for evidence_id in sorted(
            {
                "WP01:public_audit_build",
                "WP01:baseline_tests",
                "WP01:licensed_adapter_build",
                "WP01:launch_smoke",
                "WP01:artifact_hash_provenance",
                "WP01:agileplus_evidence_record",
            }
        )
    ]
    valid_base = {**base, "commands": [{"command_id": "run"}], "evidence": valid_evidence}
    valid_evidence[0]["command_ids"] = [{}]
    manifest.write_text(json.dumps(valid_base))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "command_ids must be a list of non-empty strings" in result.stderr

    valid_evidence[0]["command_ids"] = ["run"]
    valid_evidence[0]["artifact_ids"] = [{}]
    manifest.write_text(json.dumps(valid_base))
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "artifact_ids must be a list of non-empty strings" in result.stderr
