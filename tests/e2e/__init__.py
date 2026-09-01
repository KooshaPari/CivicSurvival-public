"""End-to-end test entry point.

These tests are intended to run **inside** the CS2 runtime via the
private CS2 Modding Test Framework. This public mirror is a **source
mirror only** -- there is no CS2 runtime here -- so the actual E2E
tests live in the closed-source QA harness.

What this directory provides on the public side:

* A canonical location for the scorecard's E2E pillar (29).
* A stub module that imports cleanly so the public test suite does
  not break.
* A contract: any test in `tests/e2e/test_*.py` that uses the
  `@pytest.mark.e2e` marker is exempted from the standard pytest
  testpaths restriction and run in the closed-source CI instead.

If you are a closed-source QA contributor, see the `/closed/e2e/`
directory for the actual test code that runs against the CS2 runtime.
"""

__all__: list[str] = []
