# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `scripts/release.py` for atomic version bumps (#51) — `307d3d9`
- Community profile files: `CODEOWNERS`, `dependabot.yml`, issue/PR templates, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md` (#55) — `c0097bd`
- `.civicignore` manifest and updated WP01 evidence for the current SHA (#56) — `e27d055`

### Changed

- CI workflows now use `cancel-in-progress` concurrency (#49) — `2aa9033`
- `README.md` now displays the "AI slop inside" and total-downloads badges (#50) — `e25b1a0`
- `.gitignore` now excludes Python `__pycache__` directories (#48) — `0bc641c`
- Civic docs record the worktree reconciliation gate (#54) — `10de20f`

### Fixed

- `public-audit` now catches `PublishConfiguration.xml` version drift (#53) — `2aadd4d`
- Dependency delta scan exempts metadata-only `.csproj` changes (#47) — `4f34815`
- Localization allowlist drift is now self-discovered via `LEGIT_IDENTICAL` (#52) — `f9d9e0b`

## [0.3.25] - 2026-08-31

### Added

- Runnable public evidence lane for the audit subsystem (#5) — `ad41d7f`
- 88-pillar OpenSSF Scorecard workflow for CI regression prevention — `8cb6f4c`
- `plan.md` + `meta.json` for all 10 AgilePlus specs — `77b61f3`
- 10 AgilePlus specs for the CivicSurvival mod — `ab3478b`
- `CLAUDE.md` repository guidance for AI assistants — `32518d2`
- Infisical integration workflow — `e199d39`
- CircleCI parallel pipeline — `f570e99`
- Trunk.io lint/format configuration — `4062a33`
- GitHub Actions CI on Blacksmith runners — `a0d4d2c`
- Mergify auto-merge rules (zero-review policy) — `f87207d`
- CI workflow stable lint/test gate names — `5e01076`, `e7d7e7d`
- `.pre-commit-config.yaml`, `renovate.json`, `.trunk/trunk.yaml`, and `.github/stale.yml` baseline — `a4b7275`, `1b6f958`, `ddb5ff1`, `a541ffc`
- Initial `scorecard.yml`, `trunk-check.yml`, and `ci.yml` workflows — `877335f`, `fa15115`, `8ee72bf`
- Localization regression test suite (#46) — `ee8bfc9`

### Changed

- Version bumped to `0.3.25` (#46) — `ee8bfc9`
- Contracts now multi-target CS2 `net48` and modern audit targets (#21) — `8caaf30`
- Mergify configuration upgraded to current format (#25) — `68a7aa1`
- WP02-A audit reformatted — `755b994`
- WP01 reassessment reformatted — `4d92793`
- Reconciled-intent section reformatted — `f42dab9`
- Civic docs: warfare program specification preserved (#3) — `5f9f37d`
- Civic docs: current hosted state reconciled (#30) — `87214f0`
- Civic docs: licensed-host build boundary recorded (#26) — `d258ae4`

### Fixed

- OpenSSF Scorecard: align Markdown baseline evidence (#44) — `ed78823`
- CI: verify the pinned Infisical CLI artifact (#42) — `22f6036`
- CI: pin all workflow actions immutably (#41) — `1d529c9`
- Scorecard script made Ruff-clean (#43) — `4d18665`
- CI: support shrinkwrap in the public-audit cache (#40) — `b7e1770`
- Governance: require bot checks before merge (#39) — `4cfcf03`
- CI: support npm shrinkwrap dependency gates (#38) — `032285e`
- CI: require explicit Infisical sync invocation (#37) — `c2db0b1`
- Civic docs: correct current baseline evidence (#36) — `9a1a8c0`
- Mergify: migrate active commit format (#33) — `1a7a229`
- Governance: align Mergify with zero-review policy (#28) — `9d8a99c`
- CI: dependency delta scans now fail closed (#23) — `f39b7b2`
- CI: hardened Infisical logging and action pins (#24) — `f4cb64c`
- CI: reconcile PR #4 security hardening with main (#13) — `5970534`
- Scorecard: fix invalid `codeql-action` SHA (#12) — `f7cbed5`
- Scorecard: repair workflow — 32 consecutive failures resolved (#11) — `fa05d69`
- CI: resolve scorecard workflow permissions and sync manifest version — `26442ec`
- CI: replace broken `trunk-action` with deterministic prettier-scoped check (#1) — `24ca49b`

### Dependencies

- `vite` 8.0.13 → 8.2.2 (dev) in `CivicSurvival/UI` (#16) — `cecf566`
- `brace-expansion` in `CivicSurvival/UI` (#15) — `f8d7546`
- `immutable` 5.1.5 → 5.1.9 in `CivicSurvival/UI` (#14) — `b88662e`
- `undici` 7.25.0 → 7.29.0 in `CivicSurvival/UI` (#9) — `5c1932c`
- `fast-uri` 3.1.2 → 3.1.6 (dev) in `CivicSurvival/UI` (#8) — `f341fdc`
- `js-yaml` 4.1.1 → 4.3.2 (dev) in `CivicSurvival/UI` (#7) — `d961a49`
- `postcss` 8.5.14 → 8.5.26 in `CivicSurvival/UI` (#6) — `3f34149`

## [0.3.24] - 2026-07-22

### Added

- Initial public release of CivicSurvival (`v0.3.24`) — `0b21807`

---

## Notes

- **License**: Client source is published under the
  [PolyForm Strict License 1.0.0](https://polyformproject.org/licenses/strict/1.0.0/).
  Game assets under `Assets/` are licensed separately under
  **CC BY-NC-ND** (see `Assets/LICENSE`).
- **Build**: This repository is **source-available for reading**, not a one-click
  build. See [`BUILDING.md`](BUILDING.md) for the full picture.
- **Mod**: CivicSurvival is an Infrastructure Survival Mod for
  Cities: Skylines II. Play it on
  [Paradox Mods](https://mods.paradoxplaza.com/mods/147665).

[Unreleased]: https://github.com/KooshaPari/CivicSurvival-public/compare/0.3.25...HEAD
[0.3.25]: https://github.com/KooshaPari/CivicSurvival-public/compare/0.3.24...0.3.25
[0.3.24]: https://github.com/KooshaPari/CivicSurvival-public/releases/tag/0.3.24
