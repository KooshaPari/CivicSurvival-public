---
title: Runbook
---

# Runbook

## Audit chain fails verification

1. `civic audit verify --since <last-known-good-sha>`
2. If single-append break: `civic audit amend --reason <reason>`
3. If multi-append break: escalate

## Cross-language drift test fails

1. `civic drift test --case <N>` to localize
2. Check FlatBuffers schema version vs reader
3. If schema regression: roll back reader, not schema
