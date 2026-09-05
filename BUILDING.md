# Building

**Read this first: this repository is source-complete for the Roslyn generators,
but it is not a one-click Cities: Skylines II build environment.**

The source is published for transparency and auditability. A full build of a Cities:
Skylines II mod requires a configured CS2 modding environment. The
`CivicSurvival.Analyzers` source generators are published in this snapshot and are
included as an analyzer-only project reference by `CivicSurvival.csproj`; they are
not the missing dependency described by older WP01 records. A third-party build
still requires the licensed game assemblies, CS2 Modding Toolkit, and the other
toolchain components listed below.

If you only want to verify what the mod does, just read the code. If you want to
understand the build contract anyway, the requirements below are accurate to the
project's `CivicSurvival/CivicSurvival.csproj`.

## Requirements

1. **Cities: Skylines II installed.** Provides `Game.dll` plus the Unity / Colossal /
   UnityEngine managed assemblies the project references. The build resolves these
   from the game's `…\Cities2_Data\Managed\` folder. If your game lives somewhere the
   toolchain does not auto-detect, point the build at it via the `GameManagedPath`
   MSBuild property (`-p:GameManagedPath=...`) or the `CSII_MANAGEDPATH` environment
   variable — no need to edit the `.csproj`.

2. **CS2 Modding Toolkit**, with the `CSII_TOOLPATH` environment variable set. The
   project imports `Mod.props` / `Mod.targets` from this path; without it the project
   will not load in MSBuild.

3. **Unity mod-project** (for Burst AOT). Only needed when building with Burst
   enabled (`EnableCivicBurst=true`). The build post-processor uses the Unity mod
   project to compile native Burst output.

4. **Python and Node.js** — the prebuild step runs code generators and contract
   checks (`scripts/generate.py`, `scripts/contract_check.py`,
   `Tools/generate-binding-manifest.js`, and others). These run automatically before
   compilation and will fail the build if generated artifacts are stale.

5. **UI toolchain** — Node.js with the UI's `npm` dependencies; the UI is built with
   webpack and type-checked / linted as part of the build.

## Burst is optional

The mod has a single Burst switch, `EnableCivicBurst` (in `CivicSurvival.csproj`).

- With Burst **off** (`EnableCivicBurst=false`), jobs run as managed IL and
  **Unity.Logging is not required at all** — its reference and source generator are
  gated on `EnableCivicBurst=true`, and Burst logging is behind `#if ENABLE_BURST`.
  This is the simpler configuration.
- With Burst **on** (`EnableCivicBurst=true`), the build additionally needs the
  Unity.Logging binaries (`Unity.Logging.dll`, `LoggingCommon.dll`,
  `MainLoggingGenerator.dll`). **These are not included in this repository.** They are
  Player-compiled from `com.unity.logging@1.2.1` using a local Unity Editor. Obtaining
  them is an extra step only relevant if you specifically want the Burst-compiled
  performance path.

## Public source-generator boundary

The public snapshot contains `CivicSurvival.Analyzers`, targeting `netstandard2.0`,
with the generators used by the client. Build or inspect that project independently
with:

```text
dotnet build CivicSurvival.Analyzers/CivicSurvival.Analyzers.csproj --nologo
```

The client references the project with `ReferenceOutputAssembly="false"` and
`OutputItemType="Analyzer"`, so its generated source is available during compilation.
That project build does not provide the game/toolkit assemblies or prove that a mod
loads in a licensed game.

## End-to-end build boundary

Even with the generators present, a complete client build remains environment-bound:
it requires Cities: Skylines II managed assemblies, the CS2 Modding Toolkit, and (for
the relevant configurations) the Unity/Burst and UI toolchains above. A successful
generator or contracts build is therefore source/build evidence, not licensed-host
adapter or launch-smoke evidence. WP01 remains pending until the external evidence
runbook is completed on the authorized host.
