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
    manifest = tmp_path / "evidence.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "civic.wp01.evidence", "schema_version": 1,
                "subject": {"commit": "a" * 40},
                "environment": {"host_class": "licensed-game", "license_basis": "record"},
                "artifacts": [{"artifact_id": "out", "path": "evidence.txt", "sha256": digest}],
                "commands": [{"command_id": "run"}],
                "evidence": [{"evidence_id": evidence_id, "status": "pass", "subject_commit": "a" * 40, "command_ids": ["run"], "artifact_ids": ["out"]} for evidence_id in sorted({"WP01:public_audit_build", "WP01:baseline_tests", "WP01:licensed_adapter_build", "WP01:launch_smoke", "WP01:artifact_hash_provenance", "WP01:agileplus_evidence_record"})],
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
    manifest = tmp_path / "evidence.json"
    manifest.write_text(
        json.dumps(
            {
                "schema": "civic.wp01.evidence", "schema_version": 1,
                "subject": {"commit": "a" * 40},
                "environment": {"host_class": "licensed-game", "license_basis": "record"},
                "artifacts": [{"artifact_id": "out", "path": "evidence.txt", "sha256": digest}],
                "commands": [{"command_id": "run"}],
                "evidence": [{"evidence_id": evidence_id, "status": "pass", "subject_commit": "a" * 40, "command_ids": ["run"], "artifact_ids": ["out"]} for evidence_id in sorted({"WP01:public_audit_build", "WP01:baseline_tests", "WP01:licensed_adapter_build", "WP01:launch_smoke", "WP01:artifact_hash_provenance", "WP01:agileplus_evidence_record"})],
                "decision": {"result": "GO"},
            }
        )
    )
    result = run(tmp_path, manifest)
    assert result.returncode == 1
    assert "sha256 mismatch" in result.stderr
