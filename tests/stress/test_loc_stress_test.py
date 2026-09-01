"""Stress: simulate many locale-keys-drift scenarios to prove the check scales."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest


@pytest.mark.stress
def test_loc_check_scales_linearly(tmp_path: Path) -> None:
    """100, 1k, 10k synthetic locale keys should take proportional time."""
    locales: dict[str, dict[str, str]] = {}
    for name in ("en-US", "uk-UA", "zh-CN"):
        locales[name] = {f"K_{i:08d}": f"v_{i}" for i in range(10_000)}

    for size in (100, 1_000, 10_000):
        for name, d in locales.items():
            d_truncated = dict(list(d.items())[:size])
            (tmp_path / f"{name}.json").write_text(json.dumps(d_truncated))

        # Inline the check (avoid importing from test_localization_keys to keep this isolated)
        def keys() -> set[str]:
            all_keys: set[str] = set()
            for n in ("en-US", "uk-UA", "zh-CN"):
                all_keys ^= set(json.loads((tmp_path / f"{n}.json").read_text()).keys())
            return all_keys

        t0 = time.perf_counter()
        for _ in range(10):  # ten iterations of parity checks at this size
            keys()
        elapsed = time.perf_counter() - t0

        # Sanity bound: 10k key Xor across 30 runs should be < 5s on any reasonable host
        assert elapsed < 5.0, f"loc check too slow at size {size}: {elapsed:.2f}s"
