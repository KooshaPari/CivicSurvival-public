"""Microbenchmarks for hot-path operations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Mirror test_release.py import convention.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import release  # noqa: E402


@pytest.mark.bench
def test_release_parse_version(benchmark) -> None:
    """Parsing a version string is a hot path during atomic writes."""
    benchmark(release.Version.parse, "0.3.25")


@pytest.mark.bench
def test_release_version_comparison(benchmark) -> None:
    """Comparison is a hot path during bump verification."""
    a = release.Version.parse("0.3.25")
    b = release.Version.parse("0.3.24")
    benchmark(lambda: a > b)


@pytest.mark.bench
def test_localization_json_load_en_us(benchmark) -> None:
    """Loading the 3,531-key en-US locale is the hot path for the loc test."""
    path = ROOT / "CivicSurvival" / "Localization" / "en-US.json"
    if not path.exists():
        pytest.skip(f"locale file missing: {path}")

    def _load():
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    benchmark(_load)
