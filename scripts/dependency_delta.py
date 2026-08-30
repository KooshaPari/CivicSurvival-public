#!/usr/bin/env python3
"""Fail-closed dependency scanners for changed Node and .NET manifests."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable, Iterable, Sequence


class DependencyDeltaError(RuntimeError):
    """A changed dependency surface could not be scanned safely."""


@dataclass(frozen=True)
class ScanCommand:
    ecosystem: str
    cwd: Path
    command: tuple[str, ...]


Runner = Callable[..., subprocess.CompletedProcess[str]]


def _relative(path: str) -> Path:
    return Path(path.replace("\\", "/"))


def _node_plan(repo: Path, changed_path: str) -> ScanCommand:
    manifest_dir = (repo / _relative(changed_path)).parent
    package_json = manifest_dir / "package.json"
    lockfile = manifest_dir / "package-lock.json"
    if not package_json.exists() or not lockfile.exists():
        raise DependencyDeltaError(
            f"{changed_path}: node: add/update package-lock.json alongside package.json "
            "so npm audit can run with a reproducible lockfile"
        )
    return ScanCommand(
        ecosystem="node",
        cwd=manifest_dir,
        command=("npm", "audit", "--package-lock-only", "--audit-level=low", "--omit=dev"),
    )


def _csharp_plan(repo: Path, changed_path: str) -> list[ScanCommand]:
    solution = repo / "CivicSurvival.sln"
    changed = repo / _relative(changed_path)
    lockfile = changed if changed.name == "packages.lock.json" else changed.parent / "packages.lock.json"
    if not solution.exists() or not lockfile.exists():
        raise DependencyDeltaError(
            f"{changed_path}: csharp: add packages.lock.json and keep CivicSurvival.sln "
            "available so restore can run in --locked-mode"
        )
    return [
        ScanCommand("csharp", repo, ("dotnet", "restore", "CivicSurvival.sln", "--locked-mode")),
        ScanCommand(
            "csharp",
            repo,
            ("dotnet", "list", "CivicSurvival.sln", "package", "--vulnerable", "--include-transitive"),
        ),
    ]


def _unsupported(changed_path: str, ecosystem: str, remedy: str) -> DependencyDeltaError:
    return DependencyDeltaError(f"{changed_path}: {ecosystem}: {remedy}")


def build_scan_plan(repo: Path, changed_files: Iterable[str]) -> list[ScanCommand]:
    """Create scanner commands, rejecting changed dependency formats without a scanner."""
    plan: list[ScanCommand] = []
    seen: set[tuple[str, Path]] = set()
    csharp_added = False

    for changed_path in sorted(set(changed_files)):
        name = _relative(changed_path).name
        if name in {"package.json", "package-lock.json"}:
            command = _node_plan(repo, changed_path)
            key = (command.ecosystem, command.cwd)
            if key not in seen:
                plan.append(command)
                seen.add(key)
        elif name.endswith(".csproj") or name == "packages.lock.json":
            if not csharp_added:
                plan.extend(_csharp_plan(repo, changed_path))
                csharp_added = True
        elif name in {"Cargo.toml", "Cargo.lock"}:
            raise _unsupported(changed_path, "rust", "add a supported Rust dependency scanner before changing this manifest")
        elif name in {"go.mod", "go.sum"}:
            raise _unsupported(changed_path, "go", "add a supported Go dependency scanner before changing this manifest")
        elif name in {"pyproject.toml", "setup.py", "requirements.txt", "Pipfile.lock", "poetry.lock"}:
            raise _unsupported(changed_path, "python", "add a supported Python dependency scanner before changing this manifest")
        elif name in {"yarn.lock", "pnpm-lock.yaml"}:
            raise _unsupported(changed_path, "node", "use package-lock.json or add a scanner for this lockfile format")
    return plan


def run_scan_plan(plan: Sequence[ScanCommand], runner: Runner = subprocess.run) -> None:
    """Execute every scanner and turn any nonzero result into a gate failure."""
    for scan in plan:
        try:
            result = runner(scan.command, cwd=scan.cwd, check=False, text=True)
        except OSError as error:
            raise DependencyDeltaError(
                f"{scan.ecosystem} scanner could not start in {scan.cwd}: {' '.join(scan.command)}: {error}"
            ) from error
        if result.returncode != 0:
            raise DependencyDeltaError(
                f"{scan.ecosystem} scanner failed in {scan.cwd}: {' '.join(scan.command)} "
                f"(exit {result.returncode})"
            )


def changed_paths(repo: Path, base: str, head: str, runner: Runner = subprocess.run) -> list[str]:
    result = runner(
        ("git", "diff", "--name-only", "--diff-filter=ACMR", base, head),
        cwd=repo,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise DependencyDeltaError(
            f"git could not determine changed dependency manifests between {base} and {head}: "
            f"{result.stderr.strip()}"
        )
    return [line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Git base commit")
    parser.add_argument("--head", required=True, help="Git head commit")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    args = parser.parse_args()

    try:
        plan = build_scan_plan(args.repo, changed_paths(args.repo, args.base, args.head))
        if not plan:
            print("No supported dependency manifest changes detected.")
            return 0
        for scan in plan:
            print(f"Running {scan.ecosystem} dependency scan: {' '.join(scan.command)}")
        run_scan_plan(plan)
    except DependencyDeltaError as error:
        print(f"Dependency Delta failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
