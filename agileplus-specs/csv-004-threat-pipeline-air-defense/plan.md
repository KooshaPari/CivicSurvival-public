# Implementation Plan: Threat Pipeline and Air Defense

## Implementation Steps

1.  **Validate Threat Trajectory Physics**: Ensure threats follow deterministic, physics-based paths.
2.  **Refine Detection Probability Models**: Factor in weather, range, and technology level for Spotters.
3.  **Complete AirDefense Engagement Rules**: Ensure probability of kill (PK) calculations are consistent.
4.  **Finalize Countermeasure Effectiveness**: Tune degradation rates for jamming and decoys.
5.  **Validate Damage Calculations**: Ensure ThreatDamage correctly cascades to infrastructure.
6.  **Performance Optimization**: Ensure the pipeline completes within the tick budget.
7.  **ThreatUI Rendering Check**: Verify real-time threat tracking doesn't cause frame drops.

## Dependencies

-   **ModState (csv-001)**: Core state for threat data.
-   **PowerGrid (csv-002)**: Air defense systems require power to operate.
-   **Waves System**: Schedules and manages the flow of incoming threats.

## Risk

-   **Tick Budget Overruns**: Complex threat pipelines could exceed the 2ms budget.
-   **Determinism Failure**: Non-deterministic calculations could break replay compatibility.
-   **Engagement Logic Errors**: Incorrect PK calculations could make threats too easy or impossible to stop.
-   **UI Lag**: Real-time rendering of many threats and interceptors could impact performance.

## Verification

-   [ ] **Trajectory Determinism**: Verify identical seeds produce identical threat paths.
-   [ ] **Detection Probability Audit**: Check that Spotters correctly factor all variables.
-   [ ] **Air Defense Simulation**: Run multiple engagement scenarios to verify PK consistency.
-   [ ] **Damage Cascade Test**: Ensure infrastructure damage matches threat impact values.
-   [ ] **Full Pipeline Benchmark**: Run a high-intensity threat wave and measure tick budget usage.
