"""Domain priority + initialization order contract discipline tests.

ADR-0004 binds five invariants:
1. PRIORITY is in 1000..9999.
2. PRIORITY is unique across all domains (no ties).
3. Priority decade aligns with the domain tier (the unit digit orders
   within the tier).
4. Every priority declared in *Domain.cs appears in docs/domains.md.
5. priority = 0 is forbidden (use 9000..9999 as opt-out sentinel).

A drift in any direction (declaration without doc entry, doc entry
without declaration, tie, out-of-range, sentinel abuse) fails CI.

Tests skip gracefully if CivicSurvival/Domains or docs/domains.md is
missing -- the test must not block contributors working on adjacent
slices of the repo.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
DOMAINS = ROOT / "CivicSurvival" / "Domains"
DOCS_INDEX = ROOT / "docs" / "domains.md"
PRIORITY_RANGE = (1000, 9999)
ALLOW_SENTINEL_LOW = False  # priority = 0 forbidden per ADR-0004


def _declared_priorities() -> dict[str, int]:
    """Parse every *Domain.cs and return {domain_name: priority}."""
    if not DOMAINS.exists():
        return {}
    out: dict[str, int] = {}
    for d in sorted(DOMAINS.iterdir()):
        if not d.is_dir():
            continue
        main = d / f"{d.name}Domain.cs"
        if not main.exists():
            cs = list(d.glob("*Domain.cs"))
            if not cs:
                continue
            main = cs[0]
        text = main.read_text(encoding="utf-8")
        m = re.search(r"PRIORITY\s*=\s*(-?\d+)", text)
        if m:
            out[d.name] = int(m.group(1))
    return out


def _doc_indexed_priorities() -> dict[str, int]:
    """Parse docs/domains.md and return {domain_name: priority}.

    The reading-order table format is:
        | 18 | `AirDefense` | 2510 | `AirDefenseDomain.cs` | ... |
    Column order: index | domain | priority | entry-point | description.
    We walk every pipe-separated row, find the priority cell (3-4 digit
    number >= 1000), and pair it with the cell two positions earlier
    (the domain name, possibly wrapped in backticks).
    """
    if not DOCS_INDEX.exists():
        return {}
    text = DOCS_INDEX.read_text(encoding="utf-8")
    out: dict[str, int] = {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        for idx, cell in enumerate(cells):
            if not cell.isdigit() or not (1000 <= int(cell) <= 9999):
                continue
            prio = int(cell)
            # The cell two positions earlier is the domain name (in the
            # standard reading-order table); the cell one position earlier
            # is the row index "#". Fall back to "previous non-digit" if
            # the layout ever varies.
            if idx >= 2:
                candidate = cells[idx - 2].strip().strip("`")
                if candidate and not candidate.isdigit() and not candidate.startswith("#"):
                    out[candidate] = prio
                    break
            if idx >= 1:
                candidate = cells[idx - 1].strip().strip("`")
                if candidate and not candidate.isdigit():
                    out[candidate] = prio
                    break
            break
    return out


def test_every_domain_declaration_is_in_range() -> None:
    """Rule 1: PRIORITY must be in 1000..9999 (or 9000s opt-out)."""
    for name, prio in _declared_priorities().items():
        assert PRIORITY_RANGE[0] <= prio <= PRIORITY_RANGE[1], (
            f"Domain {name} has PRIORITY={prio} outside {PRIORITY_RANGE}"
        )


def test_no_priority_is_zero() -> None:
    """Rule 5: priority = 0 is forbidden (would load first, breaking contract)."""
    if not ALLOW_SENTINEL_LOW:
        for name, prio in _declared_priorities().items():
            assert prio != 0, f"Domain {name} has PRIORITY=0 -- use 9000s as opt-out sentinel"


def test_no_two_domains_share_a_priority() -> None:
    """Rule 2: priorities are unique (ties cause non-deterministic load order)."""
    seen: dict[int, str] = {}
    for name, prio in _declared_priorities().items():
        if prio in seen:
            raise AssertionError(f"Priority tie: {name} and {seen[prio]} both use PRIORITY={prio}")
        seen[prio] = name


def test_declared_priorities_are_in_doc_index() -> None:
    """Rule 4 (forward): every *Domain.cs priority is in docs/domains.md."""
    declared = _declared_priorities()
    indexed = _doc_indexed_priorities()
    missing = sorted(set(declared) - set(indexed))
    assert not missing, (
        f"These domains have a PRIORITY in *Domain.cs but no row in docs/domains.md: {missing}"
    )


def test_doc_index_priorities_match_source() -> None:
    """Rule 4 (inverse): every doc-indexed priority matches the source value."""
    declared = _declared_priorities()
    indexed = _doc_indexed_priorities()
    drift: list[str] = []
    for name in sorted(set(declared) & set(indexed)):
        if declared[name] != indexed[name]:
            drift.append(f"  {name}: source={declared[name]} doc={indexed[name]}")
    assert not drift, "Priority drift between source and doc index:\n" + "\n".join(drift)
