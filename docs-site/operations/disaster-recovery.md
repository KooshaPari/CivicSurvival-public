---
title: Disaster Recovery
---

# Disaster Recovery

## Snapshot schedule

- Hourly: last 24h
- Daily: last 30d
- Weekly: last 12w

## Restore

```sh
civic snapshot restore <id>
```

Verified against audit-log hash chain before completion.
