# Implementation Plan: CI Release Pipeline

## Implementation Steps

1.  **Validate GitHub Actions CI**: Ensure all workflows (C#, TS, linting, tests) pass on main.
2.  **Finalize Trunk Check**: Confirm formatting, linting, and security checks are enforced.
3.  **OpenSSF Scorecard Maintenance**: Maintain a score of 8/10 or higher.
4.  **Verify Infisical Sync**: Ensure secrets rotation is handled automatically and securely.
5.  **Optimize CircleCI Pipeline**: Fine-tune parallel build stages for faster feedback.
6.  **Complete Release Workflow**: Ensure the mod is packaged and published to Paradox Mods.
7.  **Renovate Auto-merge**: Confirm patch-level dependency updates are merged automatically.

## Dependencies

-   **CS2 Game Assemblies**: Required for C# compilation.
-   **Paradox Mods API**: For automated publishing of the .cs2mod package.
-   **GitHub/Trunk.io/Infisical**: Third-party services integrated into the CI/CD chain.

## Risk

-   **Secret Exposure**: CI must never expose game DLLs, proprietary assets, or API tokens.
-   **Flaky Tests**: Intermittent test failures could block the release pipeline.
-   **Service Downtime**: Dependence on external services could cause delays.
-   **Build Inconsistency**: Different build environments could produce different artifacts.

## Verification

-   [ ] **CI Green Check**: Ensure all 5 GitHub Actions workflows pass.
-   [ ] **Trunk Compliance**: Run a full Trunk Check and confirm zero violations.
-   [ ] **Scorecard Audit**: Verify the OpenSSF Scorecard score is 8/10 or higher.
-   [ ] **Secret Rotation Test**: Confirm Infisical successfully rotates and injects secrets.
-   [ ] **Release Artifact Test**: Verify the release workflow produces a valid .cs2mod package.
