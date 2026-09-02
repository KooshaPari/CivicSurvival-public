---
title: Deploy
---

# Deploy

Single-node Docker Compose is the recommended baseline.

```yaml
services:
  civic:
    image: ghcr.io/kooshapari/civicsurvival-public:latest
    ports: ["20129:20129"]
    volumes:
      - ./data:/app/data
      - ./audit:/app/audit
```

## Cutover checklist

1. Health: `curl http://host:20129/health` returns `{"status":"ok"}`
2. Cross-language drift test: 9/9 pass
3. Audit chain: verified, head SHA pinned
4. Disaster recovery: snapshot taken within last hour
5. Compliance: signed off

If any fails: roll back, fix, re-verify.
