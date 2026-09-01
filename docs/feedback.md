# Feedback

We use this file as a lightweight routing spec for community feedback.
For **bug reports** please use the
[bug report template](.github/ISSUE_TEMPLATE/bug_report.md) on GitHub;
for **features** use the
[feature request template](.github/ISSUE_TEMPLATE/feature_request.md);
for **vulnerability disclosure** see [SECURITY.md](SECURITY.md).

## Channels (by speed, fastest first)

| Channel | SLA | Use for |
|---|---|---|
| [Discord](https://discord.gg/) | realtime | quick questions, modder-to-modder help, alpha mod showcases |
| GitHub Issue (bug) | 7 days | reproducible bug reports with `Player.log` and mod version |
| GitHub Issue (feature) | 30 days | new domain ideas, contract proposals, governance requests |
| Email `kooshapari@gmail.com` | 14 days | private / embargoed content, partnership inquiries |
| SECURITY.md coordinated disclosure | 7 days | vulnerability disclosure -- **do not** file public issues for vulns |

## What we cannot help with here

This repository is the **public, transparent source mirror** of CivicSurvival.
The following live in the closed-source repo and are out of scope here:

* Game-server issues (stability, lag, anti-cheat false-positives).
* Paradox Mods launcher issues (download, install, sign-in).
* Player-visible gameplay bugs (capture/processing, save corruption).
* Refunds / billing / account recovery.

For those, contact Paradox support directly through the mod manager.

## Modder-visible feedback that we *do* act on here

* **API/contract changes** between releases -- if your mod breaks on
  update, file a bug with reproduction steps and we will pin the contract.
* **Localization drift** -- missing keys or stale translations affect
  the player experience; report the key + the expected value.
* **Harmony patch conflicts** with other mods -- if a published patch
  conflicts with a popular third-party mod, document the symptom.
* **Scorecard regressions** -- if a contributor accidentally removes
  a contributing file (e.g. `CODE_OF_CONDUCT.md`, `.github/CODEOWNERS`),
  the regression suite catches it, but please file an issue anyway to
  document the cause.

## What to expect

* We do not commit to issue response times; this is a side project.
* Discord is the fastest route for quick questions.
* For substantial changes, expect a 2-4 week review cycle on PRs.
* For governance/bylaws changes, see
  [phenotype-org-governance](https://github.com/KooshaPari/phenotype-org-governance).

---

Last updated: 2026-09-01.
