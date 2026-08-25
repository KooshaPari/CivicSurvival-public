# Known Issues

- The installed AgilePlus v0.2.1 CLI writes artifacts to `.agileplus/<feature>/` while its stdout still reports `kitty-specs/<feature>/`.
- The automatic research scanner is shallow and its generated report must be replaced with grounded evidence.
- AgilePlus infers false serial dependencies and noisy pseudo-file scopes from broad research prose; the reviewed `plan.md` DAG and lane task contracts supersede them.
- `flatc` is not installed in the current environment, so executable FlatBuffers schema validation is a WP02 prerequisite; structural review is recorded in `validation.md`.
- The upstream public repository is a squashed snapshot, so v0.3.23 to v0.3.24 source history is unavailable.
- WP01 root-cause evidence: the game and contracts projects previously queried `CSII_TOOLPATH` at user scope, so a documented process environment setting could not work. Contracts are now public-SDK buildable; the game adapter remains a legal local-reference build until a licensed CS2 host validates its toolchain.
- The public contracts build emits one `SYSLIB0051` warning from legacy exception serialization. It is tracked for the adapter compatibility review; it does not prevent the public audit build.
- UI dependency audit is now clean after refreshing the lockfile with `npm audit fix --package-lock-only`; CI still runs both production and full-tree audits.
- Existing C#/TS size violations are grandfathered at the measured WP01 baseline; the public policy check fails on any new violation.
