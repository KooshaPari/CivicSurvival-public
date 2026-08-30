# Licensed-host build evidence

- Date: 2026-08-30
- Repository: `KooshaPari/CivicSurvival-public`
- Host checkout: `main`
- Host commit: `8caaf30fcde00c85746b96ecca2ac47b2e7fcc16`
- Unity editor: `2022.3.62f2` (`7670c08855a9`), installed at `G:\Unity\Editor\Unity.exe`
- Unity Mod Project: generated at the configured CS2 cache path
- Entities source generators: `com.unity.entities@1.3.10`, present

## Commands

The host used the stable SDK explicitly, with a fresh package cache:

```text
dotnet exec C:\Program Files\dotnet\sdk\8.0.419\dotnet.dll restore CivicSurvival.sln --packages C:\Users\koosh\NuGetFresh
dotnet exec C:\Program Files\dotnet\sdk\8.0.419\dotnet.dll build CivicSurvival.sln --no-restore --packages C:\Users\koosh\NuGetFresh
```

## Result

- `CivicSurvival.Contracts` `net48`: passed
- `CivicSurvival.Contracts` `net8.0`: passed
- Full `CivicSurvival` mod build: failed with 261 compiler errors

The failures are unresolved private/runtime adapter symbols, including
`NullShadowWalletService`, `NullDefensePolicyReader`,
`NullThreatAudioService`, `NullThreatArrivalSource`, and
`NullOperationSlotReader`, plus DTO members absent from the public snapshot.

## Gate interpretation

This is a `HOST_PRIVATE_SOURCE_REQUIRED` result, not a Unity/toolchain failure.
The public repository remains contract-buildable and auditable. Production
warfare implementation and runtime qualification remain blocked until the
private adapter/source payload is available on the licensed host.
