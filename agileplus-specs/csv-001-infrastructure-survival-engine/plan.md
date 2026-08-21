# Implementation Plan: Infrastructure Survival Engine

## Implementation Steps

1.  **Finalize ModState Singleton**: Complete thread-safe batched writes and ensure full visibility for all 29 domains.
2.  **Complete CIVIC_PERF Instrumentation**: Implement tick budget tracking and expose metrics via the UI.
3.  **Validate Save/Load Integration**: Perform round-trip testing to ensure ModState survives CS2 save cycles.
4.  **Refine Difficulty Presets**: Verify all 5 tiers (Casual through Catastrophic) correctly apply multipliers to EngineConstants.
5.  **Harmony Patch Audit**: Ensure all patches are correctly prefixed/suffixed and removed on unload.
6.  **Cross-Domain Interaction Testing**: Validate that all 29 domains can read/write ModState without race conditions.
7.  **Performance Profiling**: Maintain tick budget under 2ms across all active domains.

## Dependencies

-   **Lib.Harmony 2.2.2**: Required for runtime patching of CS2 assemblies.
-   **Colossal Order Assemblies**: Accessed via `$(GameManagedPath)`.
-   **Paradox Mods Loader**: Entry point for the mod.

## Risk

-   **Save Format Compatibility**: Future CS2 updates may break ModState serialization.
-   **Harmony Conflicts**: Overlapping hooks with other mods could cause crashes.
-   **Performance Overheads**: Complex state management could exceed tick budgets.
-   **Thread Safety**: Concurrent access to ModState from different domains could lead to corruption.

## Verification

-   [ ] **Unit Tests**: Verify ModState thread safety and data integrity.
-   [ ] **Integration Tests**: Automated save/load round-trip tests.
-   [ ] **Manual QA**: Validate all 5 difficulty presets in-game.
-   [ ] **Performance Benchmarks**: CIVIC_PERF reports showing tick budget compliance.
-   [ ] **Unload Verification**: Confirm all Harmony hooks are removed on mod disable.
