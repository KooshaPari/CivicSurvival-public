# Implementation Plan: Diplomacy Intel Mobilization

## Implementation Steps

1.  **Finalize Diplomacy Treaty Logic**: Ensure negotiations produce deterministic outcomes.
2.  **Complete Intel Operation Mechanics**: Validate success/failure probabilities for espionage.
3.  **Refine Mobilization Scaling**: Ensure military recruitment scales with population and resources.
4.  **Integrate NeighborEnvy**: Model diplomatic pressure from adjacent cities.
5.  **Finalize Refugee Flow Handling**: Integrate displaced populations with housing and social services.
6.  **Diplomacy UI Development**: Create a clear interface for foreign relations and negotiations.
7.  **Performance Validation**: Ensure AI and refugee calculations are batched per tick and deterministic.

## Dependencies

-   **ModState (csv-001)**: Core state for diplomatic and military data.
-   **Economics (csv-005)**: Trade agreements directly affect the economy.
-   **ThreatPipeline (csv-004)**: Military readiness is key to threat response.

## Risk

-   **AI Nondeterminism**: Diplomatic AI must be identical across runs for replay.
-   **Refugee Overload**: High refugee counts could impact performance if not batched correctly.
-   **Balance of Power**: Incorrect mobilization scaling could make military forces useless or overpowered.
-   **UI Complexity**: Representing complex international relations in a clear, accessible way.

## Verification

-   [ ] **Treaty Determinism Test**: Verify identical states produce the same outcomes.
-   [ ] **Intel Operation Audit**: Confirm success rates match configured probabilities.
-   [ ] **Mobilization Scaling Test**: Ensure military size reflects available resources.
-   [ ] **NeighborEnvy Simulation**: Verify diplomatic pressure influences player decisions.
-   [ ] **Refugee Integration Test**: Ensure refugee flows are handled without performance degradation.
