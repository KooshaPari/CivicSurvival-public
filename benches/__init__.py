"""Performance benchmarks using pytest-benchmark.

These benchmarks guard against accidental perf regressions in hot paths:
- Localization key lookup
- Scorecard run latency
- Release CLI single-file surface parse

Run with: pytest -m bench benches/
Compare with: pytest-benchmark compare 0.3.24 0.3.25
"""

__all__: list[str] = []
