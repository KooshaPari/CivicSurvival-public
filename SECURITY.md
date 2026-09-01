# Security Policy

## Supported Versions

Civic Survival is currently in **Early Access beta** and is updated frequently.
Only the latest released version receives security fixes.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Civic Survival, **please report it
privately** — do not open a public GitHub issue.

**Email:** <kooshapari@gmail.com>
**Subject prefix:** `[SECURITY] Civic Survival`

Please include:

1. A clear description of the vulnerability and its impact.
2. Steps to reproduce (preferably with a save file or short clip).
3. The game version, mod version, and platform.
4. Whether you intend to disclose publicly, and on what timeline.

### What to expect

- **Acknowledgement** within 72 hours of your report.
- **Status update** within 7 days with our initial assessment.
- **Coordinated disclosure** — we will work with you on a fix-and-disclose
  timeline. We follow the principle of giving reporters reasonable time to
  publish before the public fix lands.

## Scope

This is a single-player client mod for Cities: Skylines II. The mod has **no
server-side component** and **no telemetry backend** that holds user data. The
threat model is therefore narrow:

- **Save-file integrity** — preventing save corruption / data loss.
- **Local-only data** — the mod does not phone home, but uses optional
  Discord webhooks for notifications (see `PRIVACY.md`).
- **Mod-loading safety** — the mod runs inside the host game's process;
  any native-code paths are reviewed for stability, not sandboxed security.

Issues that fall **outside** this policy's scope include:

- Game engine bugs unrelated to mod behavior.
- Crashes that only reproduce in modified `Assets/` directories you maintain
  locally.
- Performance regressions without functional impact.

## Disclosure Policy

We follow a **coordinated disclosure** model. We will not pursue legal action
against researchers who:

- Make a good-faith effort to avoid privacy violations and disruption to other
  users.
- Only interact with accounts they own or with explicit permission from the
  account holder.
- Stop testing immediately and notify us on encountering a vulnerability.
- Do not exploit a vulnerability beyond what is necessary to demonstrate it.
