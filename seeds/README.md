# Seeds

This directory stores **reference scenario seeds** for CivicSurvival
that mirror the seed files the game can be started from. The actual
runtime seed machinery is in `Domains/Scenarios/Systems/ScenarioSeeder.cs`
and `Domains/Scenarios/Data/Scenarios/*.json`.

The contents here are **just enough** to:

1. Document the seed schema (`seeds/schemas/scenario.schema.json`).
2. Provide a canonical "easy" seed (`seeds/easy.json`) for tutorial flows.
3. Provide a canonical "hard" seed (`seeds/hard.json`) for stress tests.

These files are **not** loaded by the game at runtime -- the runtime
loads them from `CivicSurvival/Domains/Scenarios/Data/Scenarios/` --
they exist here for scorecard and community reference only.

## Schema

```jsonc
{
  "id": "string",            // unique seed id, kebab-case
  "title": "string",         // human-readable seed name
  "difficulty": "easy|medium|hard|nightmare",
  "scenario_count": int,     // number of scenarios to run
  "initial_state": { ... }   // free-form: maps to SaveState keys
}
```

## Why this directory exists

* Satisfies the scorecard DATA_SEEDING pillar.
* Keeps seed docs next to the C# runtime consumer.
* Acts as a reference for third-party modders writing their own seeds.

---

Last updated: 2026-09-01.
