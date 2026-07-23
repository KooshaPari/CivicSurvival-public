# Known Issues

- The installed AgilePlus v0.2.1 CLI writes artifacts to `.agileplus/<feature>/` while its stdout still reports `kitty-specs/<feature>/`.
- The automatic research scanner is shallow and its generated report must be replaced with grounded evidence.
- AgilePlus infers false serial dependencies and noisy pseudo-file scopes from broad research prose; the reviewed `plan.md` DAG and lane task contracts supersede them.
- `flatc` is not installed in the current environment, so executable FlatBuffers schema validation is a WP02 prerequisite; structural review is recorded in `validation.md`.
- The upstream public repository is a squashed snapshot, so v0.3.23 to v0.3.24 source history is unavailable.
- The public C# audit build and baseline C# tests do not yet exist; this is the blocking WP01 gate.
