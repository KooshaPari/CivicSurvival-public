"""Release prep: bump the CivicSurvival version across the four tracked surfaces.

The version is duplicated in four places and must stay in lockstep:

* ``CivicSurvival/CivicSurvival.csproj`` -- ``<Version>``
* ``CivicSurvival/manifest.json`` -- ``version_number``
* ``CivicSurvival/Properties/PublishConfiguration.xml`` -- ``<ModVersion>`` and
  the inline ``<ChangeLog>`` summary that Paradox shows in the launcher
* ``CivicSurvival/Properties/CHANGELOG.md`` -- a ``## vX.Y.Z`` section prepended
  at the top

This script keeps them consistent. The public-audit gate (``public-audit.yml``
> scripts/ci/check-public-audit.mjs) cross-validates the first three; the
fourth is a separate human-facing changelog that ships in the Paradox Mods
package. Bumping them by hand is error-prone: a missed file is a silent drift
that only surfaces at release time.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Version parsing and validation
# ---------------------------------------------------------------------------

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, raw: str) -> "Version":
        match = VERSION_RE.match(raw.strip())
        if not match:
            raise ValueError(f"invalid version {raw!r}: expected MAJOR.MINOR.PATCH (digits only)")
        return cls(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReleasePaths:
    """The four tracked surfaces, all relative to the repo root."""

    csproj: Path
    manifest: Path
    xml: Path
    changelog: Path

    @classmethod
    def for_repo(cls, repo: Path) -> "ReleasePaths":
        return cls(
            csproj=repo / "CivicSurvival" / "CivicSurvival.csproj",
            manifest=repo / "CivicSurvival" / "manifest.json",
            xml=repo / "CivicSurvival" / "Properties" / "PublishConfiguration.xml",
            changelog=repo / "CivicSurvival" / "Properties" / "CHANGELOG.md",
        )


# ---------------------------------------------------------------------------
# Readers -- one per surface, each returns a single source-of-truth string.
# ---------------------------------------------------------------------------

_CSPROJ_VERSION_RE = re.compile(r"<Version>\s*([0-9]+\.[0-9]+\.[0-9]+)\s*</Version>", re.IGNORECASE)
_XML_MOD_VERSION_RE = re.compile(r'<ModVersion\s+Value="([0-9]+\.[0-9]+\.[0-9]+)"\s*/>')


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_csproj_version(paths: ReleasePaths) -> Version | None:
    match = _CSPROJ_VERSION_RE.search(_read_text(paths.csproj))
    return Version.parse(match.group(1)) if match else None


def read_manifest_version(paths: ReleasePaths) -> Version | None:
    data = json.loads(_read_text(paths.manifest))
    raw = data.get("version_number")
    return Version.parse(str(raw)) if raw else None


def read_xml_mod_version(paths: ReleasePaths) -> Version | None:
    match = _XML_MOD_VERSION_RE.search(_read_text(paths.xml))
    return Version.parse(match.group(1)) if match else None


def read_current_version(paths: ReleasePaths) -> Version | None:
    """Return the version if all three program surfaces agree, else None."""
    versions = {
        read_csproj_version(paths),
        read_manifest_version(paths),
        read_xml_mod_version(paths),
    }
    return next(iter(versions)) if len(versions) == 1 else None


# ---------------------------------------------------------------------------
# Writers -- each updates exactly one surface, idempotently.
# ---------------------------------------------------------------------------


def write_csproj_version(paths: ReleasePaths, version: Version) -> None:
    text = _read_text(paths.csproj)
    new_text, count = _CSPROJ_VERSION_RE.subn(f"<Version>{version}</Version>", text, count=1)
    if count == 0:
        raise FileNotFoundError(f"no <Version> element found in {paths.csproj}")
    paths.csproj.write_text(new_text, encoding="utf-8")


def write_manifest_version(paths: ReleasePaths, version: Version) -> None:
    data = json.loads(_read_text(paths.manifest))
    data["version_number"] = str(version)
    paths.manifest.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_xml_mod_version(paths: ReleasePaths, version: Version) -> None:
    text = _read_text(paths.xml)
    new_text, count = _XML_MOD_VERSION_RE.subn(f'<ModVersion Value="{version}" />', text, count=1)
    if count == 0:
        raise FileNotFoundError(f"no <ModVersion> element found in {paths.xml}")
    paths.xml.write_text(new_text, encoding="utf-8")


def write_xml_changelog_summary(paths: ReleasePaths, summary: str) -> None:
    """Replace the inline ``<ChangeLog>...</ChangeLog>`` summary in the XML.

    The summary is the one-line release note that Paradox shows in the mod
    launcher; it does not include bullets.
    """
    text = _read_text(paths.xml)
    new_text, count = re.subn(
        r"<ChangeLog>[^<]*</ChangeLog>",
        f"<ChangeLog>{summary}</ChangeLog>",
        text,
        count=1,
    )
    if count == 0:
        raise FileNotFoundError(f"no <ChangeLog> element found in {paths.xml}")
    paths.xml.write_text(new_text, encoding="utf-8")


def prepend_changelog_section(
    paths: ReleasePaths, version: Version, title: str, bullets: list[str]
) -> None:
    """Insert a new ``## vX.Y.Z`` section at the top of the markdown changelog.

    Bullets become ``- {bullet}`` list items. The existing first section is
    pushed down; the horizontal rule that separates entries is preserved.

    Callers (e.g. ``cmd_bump``) are expected to validate ``title`` and
    ``bullets`` ahead of time so this stays a pure file-rewrite helper.
    """
    text = _read_text(paths.changelog)
    lines = ["", f"## v{version} — {title.strip()}", ""]
    for bullet in bullets:
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Insert before the first existing "## v" section, or after the file's
    # preamble (lines 1-7 in the current file: comment + blank line).
    insertion = "\n".join(lines)
    match = re.search(r"^## v\d+\.\d+\.\d+\b", text, re.MULTILINE)
    if match:
        new_text = text[: match.start()] + insertion + text[match.start() :]
    else:
        # No prior entries: append at end (still preserving trailing newline).
        new_text = text.rstrip("\n") + "\n" + insertion
    paths.changelog.write_text(new_text, encoding="utf-8")


# ---------------------------------------------------------------------------
# High-level commands
# ---------------------------------------------------------------------------


def cmd_current(args: argparse.Namespace) -> int:
    paths = ReleasePaths.for_repo(args.repo)
    current = read_current_version(paths)
    if current is None:
        print(
            "release: version is inconsistent across csproj / manifest / XML",
            file=sys.stderr,
        )
        return 1
    print(str(current))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    paths = ReleasePaths.for_repo(args.repo)
    current = read_current_version(paths)
    if current is None:
        print(
            "release: version mismatch detected across csproj / manifest / XML",
            file=sys.stderr,
        )
        return 1
    print(f"release: version {current} is consistent")
    return 0


def cmd_bump(args: argparse.Namespace) -> int:
    try:
        new_version = Version.parse(args.version)
    except ValueError as exc:
        print(f"release: {exc}", file=sys.stderr)
        return 2
    paths = ReleasePaths.for_repo(args.repo)

    # Fail closed: only bump if the existing version is consistent.
    current = read_current_version(paths)
    if current is None:
        print(
            "release: refusing to bump -- existing version is inconsistent. "
            "Run `release verify` and reconcile by hand first.",
            file=sys.stderr,
        )
        return 2
    if new_version <= current:
        print(
            f"release: refusing to bump -- new version {new_version} is not "
            f"strictly greater than current {current}",
            file=sys.stderr,
        )
        return 2
    if not args.title.strip():
        print("release: --title must not be empty", file=sys.stderr)
        return 2
    if not args.bullets:
        print("release: at least one --bullet is required", file=sys.stderr)
        return 2
    if not args.summary.strip():
        print("release: --summary must not be empty", file=sys.stderr)
        return 2

    write_csproj_version(paths, new_version)
    write_manifest_version(paths, new_version)
    write_xml_mod_version(paths, new_version)
    write_xml_changelog_summary(paths, args.summary)
    prepend_changelog_section(paths, new_version, args.title, args.bullets)

    # Sanity-check the post-state: re-read everything and confirm consistency.
    post = read_current_version(paths)
    if post != new_version:
        print(
            f"release: post-bump verification failed -- read back {post}, expected {new_version}",
            file=sys.stderr,
        )
        return 1
    print(f"release: bumped {current} -> {new_version}")
    return 0


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="release",
        description="Bump and verify the CivicSurvival release version.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Path to the repository root (default: cwd)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("current", help="Print the current version, if consistent")
    sub.add_parser("verify", help="Exit 0 if all surfaces agree on the version, else 1")

    bump = sub.add_parser("bump", help="Bump the version across all surfaces")
    bump.add_argument("--version", required=True, help="New version (MAJOR.MINOR.PATCH)")
    bump.add_argument("--title", required=True, help="Heading for the new CHANGELOG.md section")
    bump.add_argument(
        "--summary",
        required=True,
        help="One-line release note written into the XML <ChangeLog> element",
    )
    bump.add_argument(
        "--bullet",
        action="append",
        default=[],
        dest="bullets",
        help="Bullet for the new CHANGELOG.md section (repeatable)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "current":
        return cmd_current(args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.command == "bump":
        return cmd_bump(args)
    parser.error(f"unknown command {args.command!r}")
    return 2  # unreachable; satisfies the type checker


if __name__ == "__main__":
    sys.exit(main())
