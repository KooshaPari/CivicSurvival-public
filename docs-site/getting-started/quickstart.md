---
title: Quickstart
---

# Quickstart

```sh
node dist/cli.js start --demo
curl -X POST http://127.0.0.1:20129/audit \
  -H "Content-Type: application/json" \
  -d '{"event":"test","actor":"you"}'
```

Expected: HTTP 201 with an audit ID. The audit chain head SHA is printed.
