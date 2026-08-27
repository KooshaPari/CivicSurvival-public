#!/usr/bin/env python3
"""Validate the licensed-host evidence required to open the WP01 gate."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


REQUIRED_EVIDENCE = {
    "WP01:public_audit_build",
    "WP01:baseline_tests",
    "WP01:licensed_adapter_build",
    "WP01:launch_smoke",
    "WP01:artifact_hash_provenance",
    "WP01:agileplus_evidence_record",
}


def fail(message: str, code: int = 1) -> int:
    print(f"WP01 evidence invalid: {message}", file=sys.stderr)
    return code


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: verify_wp01_evidence.py REPO MANIFEST", file=sys.stderr)
        return 2
    repo = Path(sys.argv[1]).resolve()
    manifest_path = Path(sys.argv[2]).resolve()
    try:
        data = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"manifest cannot be read: {exc}", 2)
    if data.get("schema") != "civic.wp01.evidence" or data.get("schema_version") != 1:
        return fail("schema_version must be 1")
    if data.get("decision", {}).get("result") != "GO":
        print("WP01 evidence pending: decision is not GO")
        return 1
    subject = data.get("subject")
    if not isinstance(subject, dict) or not isinstance(subject.get("commit"), str) or len(subject["commit"]) != 40:
        return fail("subject.commit must be a 40-character Git SHA")
    environment = data.get("environment")
    if not isinstance(environment, dict) or environment.get("host_class") != "licensed-game" or not environment.get("license_basis"):
        return fail("environment must declare a licensed-game host and license_basis")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        return fail("artifacts must be a list")
    artifact_map = {item.get("artifact_id"): item for item in artifacts if isinstance(item, dict)}
    if len(artifact_map) != len(artifacts):
        return fail("artifact IDs must be unique")
    for artifact in artifacts:
        if not all(isinstance(artifact.get(key), str) and artifact[key] for key in ("artifact_id", "path", "sha256")):
            return fail("each artifact needs artifact_id, path, and sha256")
        if len(artifact["sha256"]) != 64 or artifact["sha256"] != artifact["sha256"].lower() or any(char not in "0123456789abcdef" for char in artifact["sha256"]):
            return fail(f"invalid sha256 for {artifact['artifact_id']}")
        path = (repo / artifact["path"]).resolve()
        if repo not in path.parents or not path.is_file():
            return fail(f"artifact path is missing or outside repo: {artifact['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            return fail(f"sha256 mismatch for {artifact['path']}")
    commands = data.get("commands")
    command_ids = {item.get("command_id") for item in commands if isinstance(item, dict)} if isinstance(commands, list) else set()
    if not isinstance(commands, list) or len(command_ids) != len(commands):
        return fail("commands must be a list with unique command_id values")
    evidence = data.get("evidence")
    evidence_ids = {item.get("evidence_id") for item in evidence if isinstance(item, dict)} if isinstance(evidence, list) else set()
    if evidence_ids != REQUIRED_EVIDENCE:
        return fail(f"evidence IDs must be exactly {sorted(REQUIRED_EVIDENCE)}")
    for item in evidence:
        if item.get("status") != "pass" or item.get("subject_commit") != subject["commit"]:
            return fail(f"evidence {item.get('evidence_id')} must pass for the subject commit")
        if not item.get("command_ids") or not set(item["command_ids"]).issubset(command_ids):
            return fail(f"evidence {item.get('evidence_id')} references unknown commands")
        if not item.get("artifact_ids") or not set(item["artifact_ids"]).issubset(artifact_map):
            return fail(f"evidence {item.get('evidence_id')} references unknown artifacts")
    print(f"WP01 evidence accepted structurally: {len(evidence)} evidence records and {len(artifacts)} artifacts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
