#!/usr/bin/env python3
"""Validate the licensed-host evidence required to open the WP01 gate."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


REQUIRED_EVIDENCE = {
    "WP01:public_audit_build",
    "WP01:baseline_tests",
    "WP01:licensed_adapter_build",
    "WP01:launch_smoke",
    "WP01:artifact_hash_provenance",
    "WP01:agileplus_evidence_record",
    "WP01:conditional_go_no_go_pass",
}


def reject_duplicate_keys(pairs):
    """Reject ambiguous JSON objects instead of silently accepting the last key."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


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
        data = json.loads(manifest_path.read_text(), object_pairs_hook=reject_duplicate_keys)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return fail(f"manifest cannot be read: {exc}", 2)
    if not isinstance(data, dict):
        return fail("manifest top level must be an object")
    if (
        data.get("schema") != "civic.wp01.evidence"
        or type(data.get("schema_version")) is not int
        or data["schema_version"] != 1
    ):
        return fail("schema_version must be 1")
    decision = data.get("decision")
    if not isinstance(decision, dict):
        return fail("decision must be an object")
    if decision.get("result") != "GO":
        print("WP01 evidence pending: decision is not GO")
        return 1
    subject = data.get("subject")
    subject_commit = subject.get("commit") if isinstance(subject, dict) else None
    if not isinstance(subject_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", subject_commit):
        return fail("subject.commit must be a lowercase 40-character Git SHA")
    try:
        resolved_head = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--verify", "HEAD^{commit}"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return fail(f"repository HEAD cannot be resolved: {exc}")
    if resolved_head.returncode != 0:
        return fail("repository HEAD cannot be resolved")
    current_head = resolved_head.stdout.strip()
    if subject_commit != current_head:
        return fail(f"subject.commit does not match repository HEAD ({current_head})")
    environment = data.get("environment")
    if (
        not isinstance(environment, dict)
        or environment.get("host_class") != "licensed-game"
        or not environment.get("license_basis")
    ):
        return fail("environment must declare a licensed-game host and license_basis")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        return fail("artifacts must be a list")
    for artifact in artifacts:
        if (
            not isinstance(artifact, dict)
            or not isinstance(artifact.get("artifact_id"), str)
            or not artifact["artifact_id"]
        ):
            return fail("each artifact needs a non-empty string artifact_id")
    artifact_map = {item["artifact_id"]: item for item in artifacts}
    if len(artifact_map) != len(artifacts):
        return fail("artifact IDs must be unique")
    for artifact in artifacts:
        if not all(
            isinstance(artifact.get(key), str) and artifact[key]
            for key in ("artifact_id", "path", "sha256")
        ):
            return fail("each artifact needs artifact_id, path, and sha256")
        if (
            not isinstance(artifact.get("size_bytes"), int)
            or isinstance(artifact["size_bytes"], bool)
            or artifact["size_bytes"] < 0
        ):
            return fail(f"artifact {artifact.get('artifact_id')} needs a non-negative size_bytes")
        if (
            len(artifact["sha256"]) != 64
            or artifact["sha256"] != artifact["sha256"].lower()
            or any(char not in "0123456789abcdef" for char in artifact["sha256"])
        ):
            return fail(f"invalid sha256 for {artifact['artifact_id']}")
        path = (repo / artifact["path"]).resolve()
        if repo not in path.parents or not path.is_file():
            return fail(f"artifact path is missing or outside repo: {artifact['path']}")
        if path.stat().st_size != artifact["size_bytes"]:
            return fail(f"size_bytes mismatch for {artifact['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            return fail(f"sha256 mismatch for {artifact['path']}")
    commands = data.get("commands")
    if not isinstance(commands, list) or any(not isinstance(item, dict) for item in commands):
        return fail("commands must be a list of objects")
    command_values = [item.get("command_id") for item in commands]
    if any(not isinstance(command_id, str) or not command_id for command_id in command_values):
        return fail("commands must have non-empty string command_id values")
    command_ids = set(command_values)
    if len(command_ids) != len(commands):
        return fail("commands must have unique non-empty command_id values")
    evidence = data.get("evidence")
    if not isinstance(evidence, list) or any(not isinstance(item, dict) for item in evidence):
        return fail("evidence must be a list of objects")
    evidence_values = [item.get("evidence_id") for item in evidence]
    if any(not isinstance(evidence_id, str) or not evidence_id for evidence_id in evidence_values):
        return fail("evidence must have non-empty string evidence_id values")
    evidence_ids = set(evidence_values)
    if len(evidence_ids) != len(evidence) or evidence_ids != REQUIRED_EVIDENCE:
        return fail(f"evidence IDs must be exactly {sorted(REQUIRED_EVIDENCE)}")
    for item in evidence:
        if item.get("status") != "pass" or item.get("subject_commit") != subject_commit:
            return fail(f"evidence {item.get('evidence_id')} must pass for the subject commit")
        command_refs = item.get("command_ids")
        if (
            not isinstance(command_refs, list)
            or not command_refs
            or any(not isinstance(command_id, str) or not command_id for command_id in command_refs)
        ):
            return fail(
                f"evidence {item.get('evidence_id')} command_ids must be a list of non-empty strings"
            )
        artifact_refs = item.get("artifact_ids")
        if (
            not isinstance(artifact_refs, list)
            or not artifact_refs
            or any(
                not isinstance(artifact_id, str) or not artifact_id for artifact_id in artifact_refs
            )
        ):
            return fail(
                f"evidence {item.get('evidence_id')} artifact_ids must be a list of non-empty strings"
            )
        if not set(command_refs).issubset(command_ids):
            return fail(f"evidence {item.get('evidence_id')} references unknown commands")
        if not set(artifact_refs).issubset(artifact_map):
            return fail(f"evidence {item.get('evidence_id')} references unknown artifacts")
    print(
        f"WP01 evidence accepted structurally: {len(evidence)} evidence records and {len(artifacts)} artifacts verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
