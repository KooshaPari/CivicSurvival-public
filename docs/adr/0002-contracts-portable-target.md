# ADR-0002: Portable Contracts Targets for CS2 and Audit Consumers

- Status: Accepted
- Date: 2026-08-30
- Scope: `CivicSurvival.Contracts`

## Context

The CS2 mod project targets `net48`, while public audit and tooling consumers
run on modern .NET. Targeting Contracts only at `net8.0` makes the mod project
reference incompatible and prevents a licensed-host build.

## Decision

Target `CivicSurvival.Contracts` at `net8.0` and `net48`. Keep the game
adapter's `net48` target and consume the matching contracts assembly from the
mod, audit, and tooling surfaces.

## Rationale

The CS2 mod requires `net48`, while audit/tooling requires modern .NET. A small
`ContractMath` helper replaces framework-specific `Math.Clamp` calls in the
generated balance contract, keeping both targets behaviorally identical. The
contracts project remains free of CS2 toolchain imports.

## Consequences

- Contract code must compile for both target frameworks.
- CI builds the contracts project explicitly for `net8.0` and `net48`.
- Any runtime-specific behavior belongs in the game adapter or audit host, not
  in the shared contracts assembly.
