# CivicSurvival Public -- Justfile
#
# Equivalent to the Makefile. Provided for environments where make is
# unavailable (Windows, minimal containers). Recipes are intentionally
# identical (where possible) so contributors pick whichever runner exists.

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

PY := if `command -v python3` != "" { "python3" } else { "python" }
PYTEST := "pytest"
RUFF := if `command -v ruff` != "" { "ruff" } else { "python -m ruff" }

# Default recipe -- equivalent to `make help`
default:
    @just --list

# Run pytest (alias for `make test`)
test:
    {{PYTEST}} -q --ignore=tests/public-audit

# Run pytest with verbose output
test-verbose:
    {{PYTEST}} -v --ignore=tests/public-audit

# Run ruff lint
lint:
    {{RUFF}} check scripts tests

# Run ruff format (auto-fix)
format:
    {{RUFF}} format scripts tests

# Run ruff format --check
format-check:
    {{RUFF}} format --check scripts tests

# Run the 88-pillar scorecard locally
scorecard:
    {{PY}} scripts/scorecard_ci.py .

# Run scorecard with --fail-on-drop
scorecard-check:
    {{PY}} scripts/scorecard_ci.py . --fail-on-drop --baseline-file .github/scorecard-baseline.json

# Print release version
release-current:
    {{PY}} scripts/release.py current

# Verify release surfaces
release-verify:
    {{PY}} scripts/release.py verify

# Full local CI parity
ci: lint format-check test scorecard
    @echo "ci: OK"
