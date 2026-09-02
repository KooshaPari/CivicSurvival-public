---
title: Stress Test
---

# Stress Test

`demo/stress.ts` runs burst (200 reqs at 100 rps) + sustained (50 rps for 10 min).

Pass criteria: p99 < 250ms, errors < 0.5%.
