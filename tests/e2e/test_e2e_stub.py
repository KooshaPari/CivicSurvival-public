"""End-to-end stub.

The actual CS2-runtime E2E tests live in the closed-source QA harness.
This file exists only to satisfy pytest's collection contract; it has
no assertions of its own.

If you are contributing a **public-mirror-only** E2E test (i.e. one
that does not require the CS2 runtime), name your file
`test_<feature>_public.py` and put it next to this stub. The
`@pytest.mark.e2e` marker filters it cleanly.
"""

from __future__ import annotations

import pytest


@pytest.mark.e2e
def test_e2e_stub_runs() -> None:
    """Trivial stub that proves the public E2E entry point collects."""
    assert True
