# Implementation Plan: Cognitive Attention Corruption

## Implementation Steps

1.  **Refine Attention Allocation Model**: Ensure citizen focus shifts correctly between competing needs.
2.  **Optimize Corruption Spread Algorithm**: Use fixed-point math to avoid nondeterminism.
3.  **Finalize Modernization-Corruption Balance**: Tune resource costs vs. corruption reduction rates.
4.  **Complete Cognitive Threat Effects**: Ensure disinformation and propaganda effects stack correctly.
5.  **Implement Cognitive Ops Batching**: Finalize batch processing for citizen cognitive updates.
6.  **Validate Cognitive Building Placement**: Optimize placement algorithms for cognitive buildings.
7.  **Finalize Cognitive UI**: Expose per-citizen and aggregate mental state to the player.

## Dependencies

-   **ModState (csv-001)**: Shared state for all cognitive metrics.
-   **Network Domain (csv-006)**: Social graph propagation of corruption.
-   **PowerGrid (csv-002)**: Power outages degrade cognitive functions.

## Risk

-   **Nondeterminism**: Floating-point math could lead to different outcomes on different machines.
-   **Performance Bottlenecks**: Batch processing for all citizens could be heavy.
-   **Balance Issues**: Modernization vs. corruption rates could feel unbalanced.
-   **UI Complexity**: Representing 29 domains of cognitive state without overwhelming the player.

## Verification

-   [ ] **Attention Metrics Test**: Verify attention degrades proportionally to crisis severity.
-   [ ] **Corruption Propagation Test**: Confirm corruption spreads through social connections as configured.
-   [ ] **Modernization Impact Test**: Validate modernization efforts reduce corruption over time.
-   [ ] **Cognitive Threat Stacking**: Ensure cognitive threats interact correctly with other stressors.
-   [ ] **UI Display Check**: Confirm per-citizen and aggregate states are displayed accurately.
