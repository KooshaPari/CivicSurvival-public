# Implementation Plan: Economics Finance Shadow Economy

## Implementation Steps

1.  **Refine GDP and Employment Models**: Ensure indicators correctly reflect infrastructure state.
2.  **Finalize Taxation and Revenue Logic**: Validate tax rate changes propagate to satisfaction and revenue.
3.  **Tune Shadow Economy Growth**: Balance growth/shrinkage based on legitimate economy health.
4.  **Integrate Trade Agreements**: Ensure Finance domain reflects Diplomacy trade agreements and sanctions.
5.  **Implement Economic UI Charts**: Develop real-time trend charts for economic indicators.
6.  **Financial State Persistence**: Validate financial data survives save/load round-trips.
7.  **Performance Validation**: Ensure economic calculations are deterministic and within tick budgets.

## Dependencies

-   **ModState (csv-001)**: Shared state for all economic metrics.
-   **PowerGrid (csv-002)**: Infrastructure failures directly impact productivity and trade.
-   **Diplomacy (csv-006)**: Trade agreements and sanctions influence the economy.

## Risk

-   **Economic Collapse Loop**: Incorrect feedback loops could cause unrecoverable death spirals.
-   **Shadow Economy Balance**: If too powerful, it makes the game too easy; if too weak, it's irrelevant.
-   **Save/Load Integrity**: Complex financial state must migrate correctly across versions.
-   **UI Data Overload**: Presenting too many indicators could overwhelm the player.

## Verification

-   [ ] **GDP Simulation**: Verify GDP correctly tracks infrastructure damage and recovery.
-   [ ] **Tax Rate Impact Test**: Confirm tax changes affect revenue and satisfaction as intended.
-   [ ] **Shadow Economy Dynamics**: Test that the shadow economy grows/shrinks appropriately.
-   [ ] **Trade Agreement Integration**: Ensure international deals influence local markets.
-   [ ] **Financial Save/Load Test**: Validate round-trip integrity for all financial data.
