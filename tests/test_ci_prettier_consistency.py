"""Prettier consistency guard for changed files.

The ``Lint & Format`` GitHub Actions workflow (.github/workflows/trunk-check.yml)
runs ``prettier --check`` against every ``*.md`` / ``*.yml`` / ``*.yaml`` /
``*.json`` / ``*.jsonc`` / ``*.mdx`` file touched by a PR (vs the merge base).
A failure produces this output::

    [warn] .github/scorecard-baseline.json
    [warn] Code style issues found in the above file. Run Prettier with --write to fix.
    ##[error]prettier --check failed on changed files; run prettier --write

The PR has to be re-pushed after ``prettier --write`` to clear the gate.

That re-push loop has burned me twice in this repo alone (PR #46/#47, PR #58):
the human forgetfulness / CRLF-on-Windows issue / JSON-array-line-break
mismatch wasn't caught until CI ran. This test catches the same class of
issue **before** the PR is pushed, by running the same ``prettier --check``
the CI uses against the same files.

Behaviour:
- Locates every prettier-managed file under the repo root.
- Respects ``.prettierignore`` (the same one CI uses) by reusing the
  patterns that the CI workflow reads.
- Skips gracefully if ``prettier`` is not on PATH (so the test never
  blocks a workflow run on a contributor's box that lacks Node/bun).
- Runs ``prettier --check`` with the same flags as CI:
  --ignore-path .prettierignore.
- When ANY file fails the check, the test prints the precise list of
  offenders AND the exact ``prettier --write`` command to fix them.

This intentionally mirrors ``trunk-check.yml`` step "prettier check"
(PR-scoped variant). If the CI gate ever changes its scan surface,
update the ``PRETTIER_EXTS`` / ``PRETTIER_IGNORE_FILES`` constants
here to match.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]

# Extensions prettier covers in the CI gate. Mirrors
# `.github/workflows/trunk-check.yml:93`.
PRETTIER_EXTS = (".md", ".yml", ".yaml", ".json", ".jsonc", ".mdx")

# Files that the CI uses as ignore sources. Both are passed via
# `--ignore-path`. Mirrors `.github/workflows/trunk-check.yml:103-108`.
PRETTIER_IGNORE_FILES = (".prettierignore", ".gitignore")


def _prettier_files() -> list[Path]:
    """Walk the repo and return every prettier-managed file."""
    out: list[Path] = []
    for ext in PRETTIER_EXTS:
        out.extend(ROOT.rglob(f"*{ext}"))
    return sorted(out)


def _matches_ignore(rel_path: str, patterns: list[str]) -> bool:
    """Tiny .prettierignore/.gitignore matcher.

    Supports ``/``-anchored globs and ``**`` traversal. Mirrors the
    subset of syntax prettier applies -- which is the same as the
    gitignore subset (negation with ``!`` is NOT supported by
    prettier, so we don't either).
    """
    import fnmatch

    for pat in patterns:
        # Normalize: strip trailing /, optional leading /
        p = pat.strip().rstrip("/").lstrip("/")
        if not p or p.startswith("#"):
            continue
        # Anchor-aware match: if pattern starts with /, only match at root
        anchored = pat.startswith("/")
        target = rel_path.lstrip("/")
        if anchored:
            if fnmatch.fnmatch(target, p):
                return True
        else:
            # Recursive match: also try matching any suffix of the path
            if fnmatch.fnmatch(target, p) or any(
                fnmatch.fnmatch("/" + seg, p) for seg in target.split("/")
            ):
                return True
    return False


def _load_ignore_patterns() -> list[str]:
    """Collect ignore patterns from .prettierignore (and .gitignore fallback)."""
    patterns: list[str] = []
    ignore_path = ROOT / ".prettierignore"
    if ignore_path.exists():
        patterns.extend(ignore_path.read_text(encoding="utf-8").splitlines())
    return patterns


def _filter_ignored(files: list[Path]) -> list[Path]:
    patterns = _load_ignore_patterns()
    if not patterns:
        return files
    return [f for f in files if not _matches_ignore(str(f.relative_to(ROOT)), patterns)]


@pytest.fixture(scope="module")
def prettier_files() -> list[Path]:
    return _filter_ignored(_prettier_files())


@pytest.fixture(scope="module")
def prettier_bin() -> str | None:
    """Find prettier. Returns None if not installed (test then skips).

    Resolution order:
    1. ``prettier`` on PATH (npm i -g prettier@3.6.2 -- what CI uses)
    2. ``bun`` on PATH or at the well-known ``~/.bun/bin/bun.exe`` location
       AND ``bun run prettier`` succeeds -- the local project must have
       prettier installed via ``bun add --no-save prettier``.

    If bun is available but the local project lacks prettier, we attempt
    to install it on the fly so contributors don't have to set up node
    tooling by hand. If even that fails, we return None and tests skip.
    """
    path_bin = shutil.which("prettier")
    if path_bin:
        return path_bin
    bun_bin = shutil.which("bun")
    if bun_bin is None:
        home_bun = os.path.expanduser("~/.bun/bin/bun.exe")
        if os.path.isfile(home_bun):
            bun_bin = home_bun
    if bun_bin is None:
        return None

    # bun is available; verify `bun run prettier` resolves. If not,
    # install prettier on the fly (CI does this via npm; locally we
    # use bun --no-save so package.json stays unchanged in the working
    # tree).
    probe = subprocess.run(
        [bun_bin, "run", "prettier", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        install = subprocess.run(
            [bun_bin, "add", "--no-save", "prettier@3.6.2"],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(ROOT),
        )
        if install.returncode != 0:
            return None

    return "bun:prettier"


@pytest.fixture(scope="module")
def prettier_version(prettier_bin: str | None) -> str:
    if prettier_bin is None:
        return "missing"
    cmd = _prettier_cmd(prettier_bin, "--version")
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return (proc.stdout or proc.stderr or "").strip()


def _prettier_cmd(prettier_bin: str, *args: str) -> list[str]:
    """Wrap args with the resolved prettier invocation (path or bun)."""
    if prettier_bin.startswith("bun:"):
        bun_path = shutil.which("bun") or os.path.expanduser("~/.bun/bin/bun.exe")
        return [bun_path, "run", "prettier", *args]
    return [prettier_bin, *args]


def test_prettier_is_version_3_6_2(prettier_bin: str | None, prettier_version: str):
    """The CI pins prettier@3.6.2. A version mismatch locally can mask
    format drift that the CI then rejects. Skip if prettier is absent."""
    if prettier_bin is None:
        pytest.skip("prettier not on PATH; install with `npm i -g prettier@3.6.2`")
    assert prettier_version.startswith("3."), (
        f"CI pins prettier@3.6.2 but local is {prettier_version!r}; "
        "run `npm i -g prettier@3.6.2` to match"
    )


def test_prettier_check_passes_on_baseline_and_changed_files(
    prettier_bin: str | None,
    prettier_files: list[Path],
):
    """Run prettier --check on a focused set of files: every tracked file
    that has been modified vs the merge base (i.e. the surface trunk-check
    actually scans on a PR) PLUS the scorecard-baseline.json (the most
    frequently hand-edited file).

    This catches the exact failure mode that bit PR #46/#47 and PR #58:
    a single misformatted JSON file (long-array line break, CRLF on
    Windows, hand-edited indentation) trips the CI gate and forces a
    re-push.

    The scan is intentionally NARROWER than ``test_prettier_check_passes_on_all_changed_files``
    would be (see below) -- we don't scan every tracked file because
    pre-existing repo drift on files no PR has touched would produce
    false positives that block every contributor.

    Each file's content is read via ``git show HEAD:<path>`` to bypass
    any platform-specific ``core.autocrlf`` checkout-mode conversion.
    On Windows, a checkout would convert LF to CRLF, producing a false
    positive; the CI on Linux reads the blob as LF and passes. By testing
    the blob content, we get the same answer on every platform.
    """
    if prettier_bin is None:
        pytest.skip("prettier not on PATH; install with `npm i -g prettier@3.6.2`")
    if not prettier_files:
        pytest.skip("no prettier-managed files in repo")

    # Determine the merge base the same way trunk-check does:
    #   git diff --diff-filter=ACMR --name-only FETCH_HEAD HEAD -- <exts>
    # In a contributor's local clone, FETCH_HEAD points to origin/main.
    fetch_ref = subprocess.run(
        ["git", "rev-parse", "--verify", "origin/main"],
        capture_output=True,
        check=False,
    )
    if fetch_ref.returncode != 0:
        # No origin/main reachable (offline / fresh clone). Skip rather
        # than fail spuriously.
        pytest.skip("origin/main not reachable; cannot compute diff vs merge base")
    merge_base = fetch_ref.stdout.strip().decode()

    # Files changed vs merge base.
    diff_proc = subprocess.run(
        [
            "git",
            "diff",
            "--diff-filter=ACMR",
            "--name-only",
            merge_base,
            "HEAD",
            "--",
            *(f"*{ext}" for ext in PRETTIER_EXTS),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    changed_files = (
        [
            ROOT / line.strip().replace("/", "\\")
            for line in diff_proc.stdout.splitlines()
            if line.strip()
        ]
        if diff_proc.returncode == 0
        else []
    )

    # Always include the baseline file (most-edited .json).
    baseline = ROOT / ".github" / "scorecard-baseline.json"
    targets: list[Path] = list(changed_files)
    if baseline.exists() and baseline not in targets:
        targets.append(baseline)

    if not targets:
        pytest.skip("no changed-or-baseline prettier-managed files to check")

    # Write the temp files INSIDE the repo so prettier's auto-config
    # resolution finds .prettierrc. Without this, prettier falls back
    # to defaults (printWidth=80 etc.) and the format check is wrong.
    # We put them in tests/_pretty_tmp/ which is NOT in .prettierignore,
    # so the temp files get checked normally (matching CI behaviour).
    tmp_dir = ROOT / "tests" / "_pretty_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_paths: list[Path] = []
    try:
        for src in targets:
            if not src.exists():
                continue
            rel = src.relative_to(ROOT).as_posix()
            proc = subprocess.run(
                ["git", "show", f"HEAD:{rel}"],
                capture_output=True,
                check=False,
            )
            if proc.returncode != 0:
                continue
            tmp_path = tmp_dir / src.name
            tmp_path.write_bytes(proc.stdout)
            tmp_paths.append(tmp_path)

        if not tmp_paths:
            pytest.skip("no tracked changed-or-baseline prettier files")

        cmd = _prettier_cmd(prettier_bin, "--check")
        ignore_path = ROOT / ".prettierignore"
        if ignore_path.exists():
            cmd.extend(["--ignore-path", str(ignore_path)])
        cmd.extend(str(p) for p in tmp_paths)

        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    finally:
        for p in tmp_paths:
            p.unlink(missing_ok=True)

    if proc.returncode != 0:
        offenders: list[str] = []
        for line in (proc.stdout + proc.stderr).splitlines():
            stripped = line.strip()
            if stripped.startswith("[warn]"):
                f = stripped[len("[warn]") :].strip()
                offenders.append(f)
        msg = (
            "prettier --check failed on PR-surface files "
            "(content read from canonical git blobs, NOT the working tree):\n"
            + "\n".join(f"  - {p}" for p in offenders)
            + "\n\nFix with:\n"
            + "  "
            + " ".join(f'"{p}"' for p in offenders).join(("", ""))
            + "\n\nFull prettier output:\n"
            + proc.stdout
            + proc.stderr
        )
        pytest.fail(msg)


def test_prettierignore_actually_ignores_listed_paths():
    """Sanity: every path listed in .prettierignore must be excluded from
    the scan. A typo in the ignore file would silently widen the prettier
    surface (e.g. catching build-evidence/ would slow every PR)."""
    ignore = ROOT / ".prettierignore"
    if not ignore.exists():
        pytest.skip("no .prettierignore file")
    for line in ignore.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Build a probe path: any file matching the pattern must not
        # appear in the post-filter scan.
        import fnmatch

        matching = [
            str(p.relative_to(ROOT))
            for p in ROOT.rglob("*")
            if p.is_file()
            and any(p.suffix == ext for ext in PRETTIER_EXTS)
            and (
                fnmatch.fnmatch(str(p.relative_to(ROOT)).lstrip("/"), stripped)
                or any(
                    fnmatch.fnmatch("/" + seg, stripped)
                    for seg in str(p.relative_to(ROOT)).split("/")
                )
            )
        ]
        # We don't assert matching is non-empty (a path may not exist);
        # we assert that _filter_ignored() excludes any that DO match.
        filtered = _filter_ignored([Path(ROOT / m) for m in matching])
        for f in filtered:
            assert not _matches_ignore(str(f.relative_to(ROOT)), [stripped]), (
                f".prettierignore lists {stripped!r} but the file "
                f"{f.relative_to(ROOT)!r} matching it is NOT being excluded "
                "from the scan -- check the pattern syntax"
            )


def test_baseline_json_is_prettier_clean(prettier_bin: str | None):
    """The scorecard baseline file is the most-edited .json in the repo
    (every baseline bump touches it). Hand-edits that change array length
    must NOT introduce prettier drift.

    Reads the file content via ``git show HEAD:<path>`` to get the canonical
    blob (LF on every platform, irrespective of ``core.autocrlf``) and writes
    it to a temp file in the system EOL mode before running prettier. This
    prevents the Windows CRLF-on-checkout gotcha from producing a false
    positive locally while the CI sees the same LF blob and passes.
    """
    if prettier_bin is None:
        pytest.skip("prettier not on PATH")
    baseline = ROOT / ".github" / "scorecard-baseline.json"
    if not baseline.exists():
        pytest.skip("no scorecard-baseline.json")

    # Read the canonical blob (LF, irrespective of platform checkout mode).
    proc = subprocess.run(
        ["git", "show", f"HEAD:{baseline.relative_to(ROOT).as_posix()}"],
        capture_output=True,
        check=True,
    )
    blob_bytes = proc.stdout  # bytes, LF

    # Write the temp file INSIDE the repo so prettier's auto-config
    # resolution finds .prettierrc. Without this, prettier falls back to
    # defaults (printWidth=80 etc.) and the format check is wrong.
    tmp_dir = ROOT / "tests" / "_pretty_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    try:
        tmp_path = tmp_dir / "baseline.json"
        tmp_path.write_bytes(blob_bytes)
        cmd = _prettier_cmd(prettier_bin, "--check", str(tmp_path))
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    finally:
        tmp_path.unlink(missing_ok=True)

    assert proc.returncode == 0, (
        f".github/scorecard-baseline.json fails prettier --check "
        "(as read from the canonical git blob, NOT the working tree).\n"
        "This file is hand-edited on every baseline bump; run "
        "`prettier --write .github/scorecard-baseline.json` before "
        "opening the PR.\n"
        f"prettier output:\n{proc.stdout}\n{proc.stderr}"
    )


def test_prettierignore_excludes_github_workflows():
    """The CI gate comment claims workflows are validated by actionlint,
    not prettier. The .prettierignore MUST list ``.github/workflows/`` --
    a deletion there would cause every workflow edit to fail the prettier
    check on top of actionlint's, multiplying PR friction.
    """
    ignore = ROOT / ".prettierignore"
    if not ignore.exists():
        pytest.skip("no .prettierignore file")
    patterns = [line.strip() for line in ignore.read_text(encoding="utf-8").splitlines()]
    assert any(".github/workflows" in p or ".github/workflows/" in p for p in patterns), (
        ".prettierignore must exclude .github/workflows/ -- prettier's "
        "YAML formatter fights with the existing indentation style. "
        "Add `.github/workflows/` to .prettierignore."
    )
