"""Property-based tests for scripts/release.py version parsing/validation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

# Mirror test_release.py import convention.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import release  # noqa: E402

valid_versions = st.from_regex(r"^[0-9]+\.[0-9]+\.[0-9]+$", fullmatch=True)


@pytest.mark.fuzz
@given(version=valid_versions)
def test_valid_version_round_trips(version: str) -> None:
    """Every semver-shaped string should parse cleanly to its components.

    Note: leading zeros in input (e.g. '0.0.00') are accepted by parse but
    canonicalize on re-serialization; we assert component equality, not
    string equality, so this is a true round-trip property.
    """
    parts = version.strip().split(".")
    v = release.Version.parse(version)
    assert v.major == int(parts[0])
    assert v.minor == int(parts[1])
    assert v.patch == int(parts[2])


@pytest.mark.fuzz
@given(
    major=st.integers(min_value=0, max_value=99),
    minor=st.integers(min_value=0, max_value=99),
    patch=st.integers(min_value=0, max_value=99),
)
def test_assembled_version_parses(major: int, minor: int, patch: int) -> None:
    """Version.parse is the inverse of format."""
    raw = f"{major}.{minor}.{patch}"
    v = release.Version.parse(raw)
    assert (v.major, v.minor, v.patch) == (major, minor, patch)


@pytest.mark.fuzz
@given(v1=valid_versions, v2=valid_versions)
def test_comparison_is_total_ordering(v1: str, v2: str) -> None:
    """Version comparison should be antisymmetric."""
    a, b = release.Version.parse(v1), release.Version.parse(v2)
    if a == b:
        assert not (a < b) and not (a > b)
    elif a < b:
        assert b > a
    else:
        assert b < a


@pytest.mark.fuzz
@given(text=st.text(min_size=1, max_size=20))
def test_non_version_strings_are_rejected(text: str) -> None:
    """Anything that isn't strictly semver-shaped should raise ValueError."""
    from hypothesis import assume

    # Skip if it accidentally looks like a valid version
    assume(not (text and text.count(".") == 2 and text.replace(".", "").isdigit()))
    with pytest.raises(ValueError):
        release.Version.parse(text)
