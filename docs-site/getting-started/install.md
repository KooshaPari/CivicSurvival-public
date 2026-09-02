---
title: Install
---

# Install

| Path | Use it for |
|------|------------|
| [On-device demo](/getting-started/on-device) | 60-second smoke test |
| [Quickstart](/getting-started/quickstart) | First audit run |
| [Deploy](/getting-started/deploy) | Production cutover |

CivicSurvival-public ships as a CLI + small HTTP audit server. Source: `https://github.com/KooshaPari/CivicSurvival-public`.

```sh
git clone https://github.com/KooshaPari/CivicSurvival-public.git
cd CivicSurvival-public
bun install
bun run build
node dist/cli.js --port 20129
```

Verify:

```sh
curl http://127.0.0.1:20129/health
```
