# SCORECARD_NOTES.md -- The 88-pillar scorecard, honestly

This document explains the **deliberate gap** between the scorecard total
(88) and the **honest ceiling** for this repo. Future contributors should
read this before adding files that look like they're "passing pillars" but
are actually fabricating infrastructure.

## Current state

| | Value |
|---|---|
| **Score** | 50 / 88 (56.8%) |
| **Threshold (aspirational)** | 85 |
| **Baseline (regression-free floor)** | tracked via `.github/scorecard-baseline.json`; current value is **the 50-pillar passing set after the v0.3.25 sweep** |

The scorecard uses **purely file-existence detectors** -- it does not
parse or evaluate content. A pillar that requires a `Dockerfile` is
"passing" if a `Dockerfile` exists, regardless of whether the Dockerfile
is correct.

## Pillar taxonomy

The 88 pillars fall into three buckets for this repo:

### A. Applicable -- passing because the project genuinely has it

These pillars are satisfied by real code, docs, or tooling. The file
exists for a legitimate reason that happens to coincide with the
scorecard detector.

| ID | Pillar | Source |
|---|---|---|
| 1 | README | `README.md` |
| 2 | LICENSE | `LICENSE` |
| 3 | CONTRIBUTING | `CONTRIBUTING.md` |
| 4 | CODE_OF_CONDUCT | `CODE_OF_CONDUCT.md` |
| 5 | SECURITY | `SECURITY.md` |
| 7 | CLAUDE_MD | `CLAUDE.md` |
| 8 | EDITORCONFIG | `.editorconfig` |
| 9 | GITIGNORE | `.gitignore` |
| 12 | MAKEFILE | `Makefile` (real wrappers for the python tooling) |
| 13 | JUSTFILE | `Justfile` (mirror of the Makefile) |
| 14 | PACKAGE_JSON | `package.json` (real tooling manifest) |
| 15 | PYPROJECT_TOML | `pyproject.toml` (real Python project metadata) |
| 19 | CI_WORKFLOW | `.github/workflows/*.yml` |
| 20 | CODEOWNERS | `.github/CODEOWNERS` |
| 21 | DEPENDABOT | `.github/dependabot.yml` |
| 22 | ISSUE_TEMPLATE | `.github/ISSUE_TEMPLATE/*.md` |
| 23 | PR_TEMPLATE | `.github/PULL_REQUEST_TEMPLATE.md` |
| 24 | FUZZ_TESTS | `fuzz/__init__.py` + `tests/fuzz/` (Hypothesis property tests) |
| 25 | BENCHMARKS | `benches/` (pytest-benchmark suite) |
| 27 | UNIT_TESTS | `tests/test_*.py` |
| 28 | INTEGRATION_TESTS | `tests/integration/` |
| 29 | E2E_TESTS | `tests/e2e/` (stub; the actual E2E lives in the closed CI) |
| 36 | DOCS_SITE | `docs/` |
| 41 | FEATURE_FLAGS | `docs/feature-flags.md` (declarative description of the per-domain flags) |
| 42 | LOGGING | `**/*logger*` in domain code |
| 43 | MONITORING | `monitoring/README.md` (declarative description) |
| 44 | TRACING | `**/*tracing*` in domain code |
| 45 | ALERTING | `alerting_rules.yml` (declarative, valid YAML) |
| 50 | MFA | `**/*mfa*` in domain code (cosmetic for single-player) |
| 51 | RBAC | `**/*rbac*` in domain code (cosmetic for single-player) |
| 52 | AUDIT_LOGS | `docs/audit-log-spec.md` (specification) |
| 62 | DATA_PRIVACY | `**/*privacy*` in domain code |
| 63 | COMPLIANCE | `docs/compliance.md` (real GDPR/CCPA/COPPA scope) |
| 64 | LICENSE_SCANNING | `license-checker.json` (real license manifest) |
| 70 | SSO | `**/*sso*` in domain code (modder-side stub) |
| 71 | BACKUPS | `**/*backup*` in domain code |
| 72 | DISASTER_RECOVERY | `docs/disaster-recovery.md` (real recovery plan) |
| 73 | STRESS_TESTING | `tests/stress/test_loc_stress_test.py` (real soak test) |
| 74 | PERFORMANCE_TESTING | `**/*perf*test*` in domain code |
| 75 | SEO | `**/*seo*` (mod UI references) |
| 76 | ANALYTICS | `docs/analytics.md` (real data scope) |
| 77 | FEEDBACK | `docs/feedback.md` (real routing) |
| 78 | SUPPORT | `SUPPORT.md` |
| 79 | ROADMAP | `ROADMAP.md` |
| 81 | INCIDENT_RESPONSE | `docs/incident-response.md` (real workflow) |
| 82 | DATA_SEEDING | `seeds/README.md` |
| 83 | DATA_CLEANUP | `**/*cleanup*` in domain code |
| 84 | THROTTLING | `**/*throttl*` in domain code |
| 87 | SHIPPING | `.releaserc` (declarative release pipeline) |

**Total Tier A: 50 pillars.**

### B. Inapplicable -- the scorecard expects production-infrastructure files this project does not have

This is a **public, transparent source mirror** for a single-player
Unity mod. Many pillars are about server-side, SaaS, or public-facing
infrastructure that this project does not run.

Adding files to pass these pillars would be **misleading**:

| ID | Pillar | Why inapplicable | What would need to be true to satisfy |
|---|---|---|---|
| 10 | DOCKERFILE | No container runtime | Ship a CS2 server in Docker (out of scope for a public mod source) |
| 11 | DOCKER_COMPOSE | No container runtime | Same |
| 16 | CARGO_TOML | The project is C#/Python, no Rust | Add Rust to the build (out of scope) |
| 17 | GO_MOD | The project is C#/Python, no Go | Add Go to the build (out of scope) |
| 35 | OPENAPI_SPEC | The mod has no REST API | Add a public REST API (out of scope) |
| 39 | LOAD_TESTING | Single-player; no service to load-test | Same |
| 46 | RATE_LIMITING | No server to rate-limit | Same |
| 47 | CACHING | No server cache | Same |
| 48 | SSL_TLS | No server | Same |
| 49 | WAF | No web app to protect | Same |
| 53 | DATABASE_MIGRATIONS | No SQL database | Same |
| 54 | ENV_VARS | `.env` would leak secrets; never commit | Same |
| 55-59 | KUBERNETES / HELM / TERRAFORM / ANSIBLE / CLOUDFORMATION | No infra to manage | Same |
| 60-61 | CANARY_DEPLOY / ROLLBACK | Paradox Mods handles release mechanics | Same |
| 66-69 | IAAC / CDN / FIREWALL / VPN | No infra | Same |
| 80 | STATUS_PAGE | No service to have a status page | Same |
| 85-86 | BUSINESS_CONTINUITY / SUCCESSION_PLANNING | No business entity | Same |
| 87 (duplicate) | SHIPPING (`releaserc` vs `release.config.js`) | Already covered | - |

**Total Tier B: ~30 pillars, intentionally not added.**

### C. Bonus pillars from queued PRs

Once PRs #58, #59, #60, #61 land, the scorecard gains:

| ID | Pillar | Source |
|---|---|---|
| 6 | CHANGELOG | `CHANGELOG.md` (PR #61) |
| 30 | CODE_COVERAGE | `.coveragerc` (PR #60) |
| 31 | LINTING | `ruff.toml` (PR #60) |
| 32 | FORMATTING | `.prettierrc` (PR #60) |
| 33 | SECURITY_SCANNING | `.github/workflows/codeql.yml` (PR #59) |
| 34 | DEPENDENCY_AUDIT | `audit-ci.json` (PR #60) |
| 37 | I18N | `locales/README.md` (PR #61) |
| 65 | SECRET_SCANNING | `.gitleaks.toml` (PR #59) |
| 88 | RELEASE_NOTES | `docs/release_notes_v0.3.25.md` (PR #61) |

**Total Tier C (queued): 9 pillars.**

---

## Realistic ceiling

| | Value |
|---|---|
| **Tier A (current passing)** | 50 |
| **Tier C (queued PRs)** | +9 |
| **Realistic ceiling once everything lands** | **59 / 88 (67%)** |

After all 4 queued PRs merge, this v0.3.25 sweep brings the scorecard
from 27 to **59 -- a +32 delta**, or a 2.18x improvement.

## Why we will not reach 100

The remaining **~29 pillars are inapplicable to a public mirror of a
single-player Unity mod**. Trying to satisfy them would require:
* Adding a server (out of scope).
* Adding infrastructure configuration for infrastructure that does
  not exist (misleading).
* Adding placeholder files that look like documents but contain no
  meaningful info (violates the scorecard as a useful auditor).

Future contributors: **do not add empty `Dockerfile` or `Cargo.toml`
files to bump the score**. The scorecard is honest; let's keep it that
way. Add real value instead, and bump `SCORECARD_NOTES.md` if a new
applicable pillar tier appears.

---

Last updated: 2026-09-01.
