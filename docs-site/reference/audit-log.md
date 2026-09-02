---
title: Audit Log Spec
---

# Audit Log Spec

Each entry:

```json
{
  "ts": "2026-09-02T16:00:00Z",
  "actor": "you",
  "event": "test",
  "prev_sha": "abc123...",
  "sha": "def456..."
}
```

`sha = sha256(prev_sha + ts + actor + canonical_event_json)`. Chain breaks on any tamper.
