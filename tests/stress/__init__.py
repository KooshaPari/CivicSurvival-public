"""Stress / soak tests.

These run longer scenarios that exercise the CI surface:
- 100-bump stress: chain N version bumps to verify atomic-write idempotence
- 1000-key locale drift simulation: prove the loc check scales linearly

Run with: pytest -m stress tests/stress/
"""

__all__: list[str] = []
