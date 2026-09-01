"""Integration tests for the CivicSurvival public mirror.

These tests exercise multi-component workflows end-to-end against a tmp
git repo and the actual scripts/release.py + scripts/dependency_delta.py +
scripts/scorecard_ci.py tooling. They are slower than the per-module unit
tests in tests/test_*.py but more thorough.

Run with: pytest -m integration tests/integration/
Skip with: pytest -m "not integration" tests/

Marked with @pytest.mark.integration so they can be filtered.
"""

__all__: list[str] = []
