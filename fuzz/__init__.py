"""Property-based fuzz tests entry point.

This thin package at the canonical `fuzz/` location re-exports the heavy
property-based suites that live under tests/fuzz/. Keeping the root-level
`fuzz/` package makes the package discoverable from any CWD while letting
pytest --rootdir=tests continue to work as before.

Run with:
    pytest tests/fuzz/                            # run only fuzz tests
    pytest -m fuzz tests/                         # filter by marker
    PYTHONPATH=fuzz:. pytest fuzz/                # run from canonical location
"""

# Re-export the public hypothesis-based test modules so they can be
# invoked from either location. This keeps imports stable across both
# package roots.
from tests.fuzz import test_release_version_fuzz as _test_release  # noqa: F401

__all__: list[str] = ["test_release_version_fuzz"]
