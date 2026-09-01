"""Fuzz / property-based tests using Hypothesis.

These tests verify invariants that should hold for arbitrary inputs --
e.g. version string format should always round-trip cleanly through
scripts/release.py; localization key normalization should be idempotent.

Run with: pytest -m fuzz tests/fuzz/
Skip with: pytest -m "not fuzz" tests/
"""

__all__: list[str] = []
