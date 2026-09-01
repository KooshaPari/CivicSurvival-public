#!/usr/bin/env python3
"""Deterministic, repository-local Civic evidence gate."""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Any

KNOWN_KINDS = {
    "all_paths_exist",
    "text_contains",
    "external_gate",
    "workflow_steps",
    "program_traceability",
    "program_dag",
}


class PolicyError(ValueError):
    pass


def load_policy(path: Path) -> dict[str, Any]:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read policy {path}: {exc}") from exc
    if not isinstance(policy, dict) or not isinstance(policy.get("version"), int):
        raise PolicyError("policy version must be an integer")
    required = policy.get("required_rule_ids")
    rules = policy.get("rules")
    if not isinstance(required, list) or not required:
        raise PolicyError("required_rule_ids must be non-empty")
    if len(required) != len(set(required)):
        raise PolicyError("required_rule_ids contains duplicates")
    if not isinstance(rules, list) or not rules:
        raise PolicyError("rules must be non-empty")
    ids: list[str] = []
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get("id"), str):
            raise PolicyError("every rule must have a string id")
        if rule["id"] in ids:
            raise PolicyError(f"duplicate rule id: {rule['id']}")
        if rule.get("kind") not in KNOWN_KINDS:
            raise PolicyError(f"unknown rule kind: {rule.get('kind')}")
        kind = rule["kind"]
        if kind == "all_paths_exist" and not _string_list(rule.get("paths")):
            raise PolicyError(f"{rule['id']} paths must be a non-empty string list")
        if kind in {"text_contains", "workflow_steps"}:
            if not isinstance(rule.get("path"), str) or not _string_list(rule.get("contains")):
                raise PolicyError(f"{rule['id']} requires a string path and contains list")
        if kind == "program_traceability":
            for field in ("paths", "requirement_paths"):
                if not _string_list(rule.get(field)):
                    raise PolicyError(f"{rule['id']} {field} must be a non-empty string list")
            if not isinstance(rule.get("task_glob"), str):
                raise PolicyError(f"{rule['id']} task_glob must be a string")
        if kind == "program_dag":
            for field in ("paths",):
                if not _string_list(rule.get(field)):
                    raise PolicyError(f"{rule['id']} {field} must be a non-empty string list")
            for field in ("plan_path", "governance_path", "go_no_go_path"):
                if not isinstance(rule.get(field), str):
                    raise PolicyError(f"{rule['id']} {field} must be a string")
        ids.append(rule["id"])
    if set(ids) != set(required):
        raise PolicyError("required_rule_ids must exactly match declared rules")
    return policy


def _string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(item, str) for item in value)


def safe_path(repo: Path, value: str) -> Path:
    candidate = (repo / value).resolve()
    try:
        candidate.relative_to(repo.resolve())
    except ValueError as exc:
        raise PolicyError(f"path escapes repository: {value}") from exc
    return candidate


def _text_probe(repo: Path, rule: dict[str, Any]) -> str | None:
    path = safe_path(repo, rule["path"])
    if not path.is_file():
        return f"missing file: {rule['path']}"
    content = path.read_text(encoding="utf-8", errors="replace")
    missing = [literal for literal in rule.get("contains", []) if literal not in content]
    return f"missing text: {', '.join(missing)}" if missing else None


def _workflow_probe(repo: Path, rule: dict[str, Any]) -> str | None:
    return _text_probe(
        repo, {"path": rule["path"], "contains": rule.get("contains", rule.get("tokens", []))}
    )


def _program_probe(repo: Path, rule: dict[str, Any]) -> str | None:
    for rel in rule.get("paths", []):
        path = safe_path(repo, rel)
        if not path.is_file():
            return f"missing program artifact: {rel}"
    return None


def _program_traceability(repo: Path, rule: dict[str, Any]) -> str | None:
    reason = _program_probe(repo, rule)
    if reason:
        return reason
    fr_text = "\n".join(
        safe_path(repo, rel).read_text(encoding="utf-8", errors="replace")
        for rel in rule.get("requirement_paths", [])
    )
    for prefix, expected in (("FR", 120), ("QR", 20)):
        values = re.findall(rf"\b{prefix}-(\d{{3}})\b", fr_text)
        unique = {int(value) for value in values}
        if unique != set(range(1, expected + 1)) or len(values) != expected:
            return f"{prefix} coverage must contain each ID 001..{expected} exactly once"
    task_paths = sorted(glob.glob(str(safe_path(repo, rule["task_glob"]))))
    ids: list[str] = []
    for task_path in task_paths:
        text = Path(task_path).read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^work_package_id:\s*(WP\d{2})\s*$", text, re.MULTILINE)
        if match:
            ids.append(match.group(1))
    if sorted(ids) != [f"WP{i:02d}" for i in range(1, 21)] or len(task_paths) != 20:
        return "program must contain exactly 20 uniquely identified WP task files"
    return None


def _program_dag(repo: Path, rule: dict[str, Any]) -> str | None:
    reason = _program_probe(repo, rule)
    if reason:
        return reason
    plan = safe_path(repo, rule["plan_path"]).read_text(encoding="utf-8", errors="replace")
    try:
        governance = json.loads(
            safe_path(repo, rule["governance_path"]).read_text(encoding="utf-8")
        )
    except (KeyError, json.JSONDecodeError, OSError) as exc:
        return f"invalid governance JSON: {exc}"
    transitions = {
        item.get("transition") for item in governance.get("rules", []) if isinstance(item, dict)
    }
    for number in range(1, 21):
        wp = f"WP{number:02d}"
        if (
            f"{wp}: Doing -> Review" not in transitions
            or f"{wp}: Review -> Done" not in transitions
        ):
            return f"governance is missing transitions for {wp}"
    go_no_go_path = rule.get("go_no_go_path")
    if go_no_go_path:
        go_no_go = (
            safe_path(repo, go_no_go_path).read_text(encoding="utf-8", errors="replace").lower()
        )
        if "conditional no-go" not in go_no_go or "licensed" not in go_no_go:
            return "WP01 go/no-go must retain the licensed-host conditional boundary"
    nodes = {f"WP{i:02d}" for i in range(1, 21)}
    edges: dict[str, set[str]] = {node: set() for node in nodes}
    in_degree = {node: 0 for node in nodes}
    declared_targets: set[str] = set()
    for line in plan.splitlines():
        if not line.lstrip().startswith("| WP"):
            continue
        fields = [field.strip() for field in line.split("|")]
        if len(fields) >= 2 and fields[1] == "WP":
            continue
        if len(fields) < 5 or fields[1] not in nodes:
            return "work-package registry contains an invalid target row"
        target = fields[1]
        declared_targets.add(target)
        dependency_field = fields[4]
        for match in re.finditer(r"WP(\d{2})(?:-WP(\d{2}))?", dependency_field):
            start = int(match.group(1))
            end = int(match.group(2) or match.group(1))
            for number in range(start, end + 1):
                source = f"WP{number:02d}"
                if source not in nodes:
                    return f"unknown DAG node: {source}"
                if target not in edges[source]:
                    edges[source].add(target)
                    in_degree[target] += 1
    if declared_targets != nodes:
        missing = ", ".join(sorted(nodes - declared_targets))
        return f"work-package registry is missing targets: {missing}"
    queue = sorted(node for node, degree in in_degree.items() if degree == 0)
    visited = 0
    while queue:
        source = queue.pop(0)
        visited += 1
        for target in sorted(edges[source]):
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)
                queue.sort()
    return None if visited == len(nodes) else "declared work-package graph contains a cycle"


def evaluate(repo: Path, policy: dict[str, Any]) -> dict[str, Any]:
    passed: list[str] = []
    failures: list[dict[str, str]] = []
    external: list[dict[str, Any]] = []
    for rule in sorted(policy["rules"], key=lambda item: item["id"]):
        rule_id = rule["id"]
        kind = rule["kind"]
        reason: str | None = None
        if kind == "all_paths_exist":
            missing = [
                value for value in rule.get("paths", []) if not safe_path(repo, value).is_file()
            ]
            reason = f"missing files: {', '.join(missing)}" if missing else None
        elif kind in {"text_contains", "workflow_steps"}:
            reason = (
                _text_probe(repo, rule) if kind == "text_contains" else _workflow_probe(repo, rule)
            )
        elif kind == "external_gate":
            external.append(
                {
                    "external": True,
                    "id": rule.get("external_id", "WP01"),
                    "state": rule.get("state", "pending"),
                }
            )
        elif kind == "program_traceability":
            reason = _program_traceability(repo, rule)
        elif kind == "program_dag":
            reason = _program_dag(repo, rule)
            if reason is None:
                external.append({"external": True, "id": "WP01", "state": "pending"})
        if reason:
            failures.append({"id": rule_id, "kind": kind, "reason": reason})
        else:
            passed.append(rule_id)
    return {
        "policy_version": policy["version"],
        "required_passed": not failures,
        "passed_rule_ids": sorted(passed),
        "failed_rules": sorted(failures, key=lambda item: item["id"]),
        "external_gates": sorted(external, key=lambda item: item["id"]),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["## Civic Evidence Gate", "", "| Rule | Status |", "|---|---|"]
    for rule_id in sorted(report["passed_rule_ids"]):
        lines.append(f"| {rule_id} | PASS |")
    for failure in report["failed_rules"]:
        lines.append(f"| {failure['id']} | FAIL: {failure['reason']} |")
    lines += ["", f"Required pass: {'yes' if report['required_passed'] else 'no'}"]
    if report["external_gates"]:
        lines += ["", "External gates:"]
        lines.extend(f"- {gate['id']}: {gate['state']}" for gate in report["external_gates"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output", choices=("json", "markdown"), default="json")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.policy)
        report = evaluate(args.repo.resolve(), policy)
    except (PolicyError, KeyError, OSError) as exc:
        print(f"civic quality gate error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(report, sort_keys=True) if args.output == "json" else render_markdown(report),
        end="" if args.output == "json" else "",
    )
    return 0 if report["required_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
