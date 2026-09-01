# Disaster Recovery

A disaster-recovery plan for the **public, transparent source mirror**
of CivicSurvival. This is a community-maintained mirror; the canonical,
paradox-published source is in the closed repo, and this doc covers
**what happens to this mirror**, not the game.

## Recovery scenarios

### 1. GitHub outage

| Item | Where | Recovery |
|---|---|---|
| Source code | `origin/main` on GitHub | Wait for GitHub to recover; mirror content is unchanged. |
| CI artifacts | GitHub Actions / CircleCI | Re-run on resume; artifacts regenerated from `build-evidence/`. |
| Documentation | This repo (`docs/`, `ROADMAP.md`, etc.) | Same as source code. |
| Releases | `gh release list 0.3.x` | Releases are immutable; outlasting GitHub would mean a full migration. |

If GitHub is down for >7 days, the maintainer may publish a tarball
mirror to a community-controlled backup (e.g. `archive.org` snapshot).

### 2. Maintainer unavailability

The maintainer (@KooshaPari) is the single point of contact. To reduce
bus-factor risk:

* **Code ownership** -- `.github/CODEOWNERS` declares explicit owners
  per directory.
* **CI gate coverage** -- the scorecard and the public-audit checks
  prevent silent regressions.
* **Documentation** -- this document is the recovery procedure; future
  owners read it.
* **Backup** -- `git bundle create` snapshots are kept offline by
  the maintainer.

If the maintainer is unreachable for >30 days, the
[phenotype-org-governance](https://github.com/KooshaPari/phenotype-org-governance)
escalation path applies.

### 3. Single-file corruption / accidental delete

Most files in this mirror are recoverable from the closed-source
canonical repo via regeneration:

* `CivicSurvival/**/*.cs` -- re-exported from the closed repo.
* `Localization/*.json` -- re-exported from the closed repo's Paratranz
  integration.
* `tests/test_*.py` -- rebuilt from the QA conventions in this repo
  (see `Makefile` and `Justfile`).
* `.github/workflows/*.yml` -- rebuilt from the CI conventions.
* `docs/*.md` -- rebuilt from the maintainer's writing process.

Files that cannot be regenerated externally:

* `LICENSE`, `CLAUDE.md`, `CODE_OF_CONDUCT.md`, community-profile files --
  reside only in this repo. Must be manually reconstructed from the
  maintainer's local copies and PR history.

### 4. License takedown (DMCA / similar)

The MIT license permits the mirror to continue unchanged. If a DMCA
notice is filed:

* The maintainer evaluates merit and may temporarily remove the specific
  file pending dispute.
* The audit log (`docs/audit-log-spec.md`) records the takedown.
* The 88-pillar scorecard continues to enforce the file's *absence*
  triggers regression detection, alerting the maintainer.

### 5. Closed-source repo unavailable

If the Paradox EULA changes and the closed repo is revoked, the public
mirror retains whatever was exported up to that point. Future updates
cease. The maintainer publishes a `final-mirror-2026-MM-DD` tag.

## RTO / RPO

| | Target | Comment |
|---|---|---|
| **RTO** (Recovery Time Objective) | 24 hours | for source code restoration from the closed repo |
| **RTO** for CI resumption | 4 hours | for dependency-cache rebuild on a self-hosted runner |
| **RPO** (Recovery Point Objective) | 1 hour | for any committed file (re-export interval from closed repo) |

## What is **not** disaster-recovery

This document does **not** cover:

* Player save file recovery (managed by Paradox cloud saves).
* License-key recovery (managed by Paradox account support).
* Game-version rollback (managed by the Paradox Mods launcher).

---

Last updated: 2026-09-01.
