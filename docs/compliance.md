# Compliance

This document records the **regulatory and policy frameworks** that
apply to the CivicSurvival public source mirror. It is the source of
truth for "what compliance regimes cover this project" so future
contributors and forks do not need to guess.

## Frameworks we are subject to

| Framework | Applies because | How we comply |
|---|---|---|
| **GDPR** | Any EU-resident player who enables the optional `SendPipeline` telemetry | `docs/analytics.md` documents what we do not collect; opt-in only; clear-text identifiers never leave the player's machine. |
| **CCPA** | California-resident players | Same as GDPR; treated identically by the opt-in + redaction pipeline. |
| **COPPA** | If any player is under 13 | The mod is rated 13+ in the Paradox Mods launcher; we do not collect data from anyone, so COPPA obligations are satisfied structurally. |
| **DMCA** | US-hosted mirror | `LICENSE` (MIT) is the canonical license; takedown requests route through `SECURITY.md`/`SUPPORT.md`. |
| **Open-source license terms (MIT)** | Self-imposed | `license-checker.json` declares the license manifest; the scorecard LICENSE pillar is locked into the baseline. |

## Frameworks we are **not** subject to

| Framework | Why not |
|---|---|
| HIPAA | We have no PHI; the project is entertainment software. |
| PCI-DSS | We never see payment data; the Paradox Mods launcher handles billing. |
| SOX | CivicSurvival is not a publicly traded company. |
| FedRAMP | Government-cloud-certification has no bearing on a single-player mod. |
| NIST 800-53 | Federal-grade controls are out of scope; we adopt CIS-style hygiene instead. |

## Branch-specific compliance

* **Public mirror (this repo)** -- MIT, GDPR/CCPA-respecting, no PHI.
* **Closed-source operations repo** -- separate license (paradox EULA + addendum); not in scope here.
* **Modder forks** -- MIT is permissive; forks may relicense at the fork author's discretion as long as the MIT attribution is preserved.

## How to change the compliance posture

1. Open a discussion issue with `[compliance]` in the title.
2. Reference this document and the specific framework.
3. Decision lives with the maintainer (see `CODEOWNERS`).
4. After resolution, this document is updated in the same PR.

---

Last updated: 2026-09-01.
