---
title: Save Format
---

# Save Format

`.civicsave` is a ZIP with three required members:

- `manifest.json` — schema version + checksums
- `intent.json` — user-stated intent at save time
- `state/` — directory tree of saved state

Self-validating: `manifest.json` lists checksums for every other member.
