# Incident Response

This document is the response procedure when a security issue is
disclosed to us. It complements `SECURITY.md` (which is the public
disclosure policy) by describing **internal** steps the maintainer
follows once a report is received.

## Severity classification

| Severity | Definition | SLA |
|---|---|---|
| **Critical** | Remote code execution, public-data exfiltration, license-key compromise | acknowledge ≤24h, fix ≤7 days |
| **High** | Privilege escalation in-game, save-data corruption | acknowledge ≤72h, fix ≤30 days |
| **Medium** | Information disclosure limited to the player, scorecard regressions | acknowledge ≤7 days, fix ≤90 days |
| **Low** | Documentation gaps, build-artifact drift | acknowledge ≤30 days, fix in next release cycle |

## Response workflow

### Phase 1: Intake (T+0 → ack)

1. Maintainer reads the disclosure via the channel specified in
   `SECURITY.md` (email or private issue).
2. Maintainer confirms receipt within the SLA above.
3. Maintainer assigns a tracking ID of the form
   `INCIDENT-YYYYMMDD-NN`.

### Phase 2: Triage (ack → 7 days)

1. Maintainer reproduces the issue.
2. Maintainer assesses severity per the table above.
3. Maintainer drafts a brief plan:
   * What is in-scope?
   * What is the minimal fix?
   * Which versions are affected?
4. For **Critical** and **High**: maintainer notifies known downstream
   mods (those in `docs/feedback.md`'s modder list) before publishing.

### Phase 3: Mitigation (triage → fix)

1. Private branch `incident/INCIDENT-YYYYMMDD-NN` cut from `main`.
2. Minimal fix committed + tested.
3. For Critical/High: maintainer cuts a hotfix release
   (e.g. `0.3.26-hotfix.1`), bypassing the normal release cadence.
4. For Medium/Low: fix lands in the next planned release.

### Phase 4: Disclosure (fix → public)

1. Maintainer coordinates public disclosure with the reporter.
2. A `docs/security-advisories/INCIDENT-YYYYMMDD-NN.md` file is
   added describing the fix timeline (no exploit details).
3. The scorecard is re-run; the new state is captured in the next
   `scripts/release.py bump` cycle.

### Phase 5: Post-mortem (post-disclosure)

1. Maintainer writes a brief post-mortem in
   `docs/post-mortems/INCIDENT-YYYYMMDD-NN.md`.
2. Action items are tracked as GitHub issues with the
   `post-mortem` label.
3. The incident is added to the `docs/incident-register.md` index.

## What this is **not**

* This is **not** a paid bug-bounty program; we do not offer bounties.
* This is **not** a 24/7 monitoring service; the maintainer is on-call
  during European business hours by default.
* This is **not** a server-IR procedure; the mod has no server.

## Audit trail

Every incident is logged to `build-evidence/audit/` with the
`incident:N id:INCIDENT-YYYYMMDD-NN severity:S` event format (see
`docs/audit-log-spec.md`).

---

Last updated: 2026-09-01.
