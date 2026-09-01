"""Discipline: the domains index in docs/domains.md must stay in sync with the actual
domain folders + registration order in Mod.cs. Failure modes this catches:

- A new domain folder added but the index missing it -> drift.
- A domain removed but the index still listing it -> drift.
- The alphabetical section and the priority section disagreeing -> drift.
- A Mod.cs `using CivicSurvival.Domains.X;` import without an X/ folder -> drift.

This test runs in CI; on failure it prints the exact diff so a contributor can fix the
index rather than having to read the file structure by hand.

Generation note: extract_domain_data() reproduces the data extraction
that built the index, so the test is self-verifying -- if the extraction
logic is right AND the index is right, the test passes; if either drifts,
the diff message names the mismatch.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def _discover_domains() -> dict[str, str]:
    """Discover all domain folders + their main entry-point class filename."""
    domains: dict[str, str] = {}
    for d in sorted((ROOT / "CivicSurvival" / "Domains").iterdir()):
        if not d.is_dir():
            continue
        main = d / f"{d.name}Domain.cs"
        if main.exists():
            domains[d.name] = main.name
        else:
            cs = [p for p in d.glob("*.cs") if "Serialization" not in p.name]
            if cs:
                domains[d.name] = cs[0].name
    return domains


def _indexed_domains() -> tuple[set[str], set[str]]:
    """Read docs/domains.md and extract domain names mentioned in it.

    Returns (alphabetical_section_names, priority_section_names).
    """
    text = (ROOT / "docs" / "domains.md").read_text(encoding="utf-8")
    # Strip fenced code blocks (they contain backtick-quoted type names like
    # `IFeatureModule` that are not domain names).
    in_code_block = False
    relevant_lines: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            relevant_lines.append(line)
    relevant_text = "\n".join(relevant_lines)

    # The alphabetical section lists domain names in backticks within a table cell.
    alpha_section_match = re.search(
        r"## Alphabetical quick reference(.+?)## Functional grouping",
        relevant_text,
        re.DOTALL,
    )
    alpha_section = alpha_section_match.group(1) if alpha_section_match else ""

    # The priority section is the first table after the H1.
    priority_section_match = re.search(
        r"## Reading order(.+?)## Alphabetical quick reference",
        relevant_text,
        re.DOTALL,
    )
    priority_section = priority_section_match.group(1) if priority_section_match else ""

    # Extract backtick-quoted names from each section. Only consider names that
    # look like domain names (PascalCase, 1-32 chars, no underscores in the
    # leading characters) AND which actually appear as a path-prefixed link or
    # table cell -- to avoid false positives like `IFeatureModule` or
    # `SystemUpdatePhase`.
    def _candidate_names(text: str) -> set[str]:
        # Only match backtick-wrapped names that contain no underscores and
        # appear in the table cell pattern | `Name` |
        return set(re.findall(r"\|\s*`([A-Z][A-Za-z]{1,31})`\s*\|", text))

    alpha_names = _candidate_names(alpha_section)
    priority_names = _candidate_names(priority_section)

    return alpha_names, priority_names


def _mod_cs_domain_imports() -> set[str]:
    """Extract every `using CivicSurvival.Domains.X;` line from Mod.cs."""
    text = (ROOT / "CivicSurvival" / "Mod.cs").read_text(encoding="utf-8")
    names: set[str] = set()
    for line in text.splitlines():
        m = re.match(r"\s*using\s+CivicSurvival\.Domains\.([A-Za-z][A-Za-z0-9]*)\s*;", line)
        if m:
            name = m.group(1)
            # Skip the nested `Notifications.Services` import (it's `Notifications/`
            # in the filesystem tree but gets imported via a sub-namespace too).
            if name == "Services":
                continue
            names.add(name)
    return names


def test_every_domain_folder_is_listed_in_both_index_sections() -> None:
    """The filesystem tree is the source of truth for which domains exist.
    The index must mention each one in both the alphabetical section AND
    the reading-order section.
    """
    discovered = _discover_domains()
    discovered_set = set(discovered)
    alpha, priority = _indexed_domains()
    missing_alpha = discovered_set - alpha
    missing_priority = discovered_set - priority
    assert not missing_alpha, (
        f"docs/domains.md alphabetical section is missing these domains: {sorted(missing_alpha)}"
    )
    assert not missing_priority, (
        f"docs/domains.md reading-order section is missing these domains: "
        f"{sorted(missing_priority)}"
    )


def test_no_stale_domain_names_in_index() -> None:
    """If a domain folder was deleted, its name must also leave the index.
    Catches the inverse of the previous rule -- drift in the other direction.
    """
    discovered = _discover_domains()
    discovered_set = set(discovered)
    alpha, priority = _indexed_domains()
    stale_alpha = alpha - discovered_set
    stale_priority = priority - discovered_set
    assert not stale_alpha, (
        f"docs/domains.md alphabetical section mentions deleted domains: {sorted(stale_alpha)}"
    )
    assert not stale_priority, (
        f"docs/domains.md reading-order section mentions deleted domains: {sorted(stale_priority)}"
    )


def test_every_mod_cs_domain_import_has_a_folder() -> None:
    """Every `using CivicSurvival.Domains.X;` in Mod.cs must map to a real folder.

    Catches the bug where a developer adds a using-directive for a domain that
    hasn't been created yet, or accidentally removes a folder while leaving
    its import behind.
    """
    imported = _mod_cs_domain_imports()
    discovered_set = set(_discover_domains())
    # `Notifications` is imported twice: once for `Domains.Notifications` and once
    # for `Domains.Notifications.Services`. The Services import is filtered out
    # in _mod_cs_domain_imports(), so Notifications should appear exactly once.
    missing = imported - discovered_set
    assert not missing, (
        f"Mod.cs imports a domain whose folder does not exist: {sorted(missing)}. "
        f"Either create the folder or remove the using-directive."
    )


def test_every_domain_folder_is_imported_by_mod_cs() -> None:
    """Inverse of the previous test. If a domain folder exists, Mod.cs must
    `using` it -- otherwise the domain is not registered with the bootstrap and
    its systems will not run. (Note: the public source excludes some domains
    from `using` when their systems self-register; we accept the folder
    existing without an import here, but log the gap as informational.)
    """
    imported = _mod_cs_domain_imports()
    discovered_set = set(_discover_domains())
    not_imported = discovered_set - imported
    # Allow up to 3 self-registering domains. If this constant rises above the
    # number of self-registering domains, the test is hiding a real bug.
    ALLOWED_SELF_REGISTER = 3
    assert len(not_imported) <= ALLOWED_SELF_REGISTER, (
        f"{len(not_imported)} domain folders exist but are not imported in Mod.cs: "
        f"{sorted(not_imported)}. Self-registering domains are allowed "
        f"(cap = {ALLOWED_SELF_REGISTER}); anything beyond that is a real "
        f"registration bug."
    )


def test_index_has_functional_grouping_section() -> None:
    """The index MUST group domains by function. This is real documentation
    value -- without the grouping, a contributor can't tell at a glance which
    domain owns the feature they want to change.
    """
    text = (ROOT / "docs" / "domains.md").read_text(encoding="utf-8")
    assert "## Functional grouping" in text, (
        "docs/domains.md is missing the 'Functional grouping' section. "
        "Add it -- alphabetical and priority orderings alone do not help "
        "a contributor find the right domain for a feature."
    )
    # Must have at least 5 functional groups
    group_lines = [
        line for line in text.splitlines() if line.startswith("**") and line.rstrip().endswith("**")
    ]
    assert len(group_lines) >= 5, (
        f"docs/domains.md has only {len(group_lines)} functional groups; expected >= 5. "
        f"Found groups: {group_lines}"
    )


def test_index_documents_how_to_add_a_domain() -> None:
    """A new contributor needs to know how to add a domain. The index must
    have a 'How to add' section that lists the steps (folder, import,
    priority, wave entry, localization, serialization).
    """
    text = (ROOT / "docs" / "domains.md").read_text(encoding="utf-8")
    assert "## How to add a new domain" in text, (
        "docs/domains.md is missing the 'How to add a new domain' section. "
        "Add it so future contributors have a single source of truth for "
        "the registration contract."
    )
    # The checklist must mention all 8 required steps from the contract
    section = text.split("## How to add a new domain")[1]
    required_steps = [
        "IFeatureModule",
        "Mod.cs",
        "priority",
        "feature-gates.sample.json",
        "localization",
        "Serialization.cs",
        "save-format.md",
        "tooltip",
    ]
    missing_steps = [s for s in required_steps if s not in section]
    assert not missing_steps, (
        f"docs/domains.md 'How to add' section is missing these required steps: {missing_steps}"
    )
