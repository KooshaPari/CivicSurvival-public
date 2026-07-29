# Research Index

See `.agileplus/civic-warfare-program/research.md`, `research/source-register.csv`, and `research/evidence-log.csv`. These are the canonical research artifacts; this session document intentionally does not duplicate them.
## WP02-A FlatBuffers verification and evolution research

- https://flatbuffers.dev/evolution/ requires fields to remain in place (or be
  deprecated), and union variants must only be appended or assigned explicit
  discriminants. This supports the checked-in explicit field IDs and the
  `RootPayload` envelope decision.
- https://flatbuffers.dev/languages/cpp/ warns that generated accessors do not
  verify untrusted offsets; a verifier must run before reading hostile or
  corrupted buffers. The future FFI gate therefore needs verifier coverage,
  bounded depth/table limits, and insufficient-buffer golden vectors.
- https://flatbuffers.dev/schema/ documents that a root is a table and unions
  add a generated discriminant field. The schema now uses a table `Envelope`
  root around the command/projection/save union rather than treating a
  projection table as the only wire root.
