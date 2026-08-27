# WP01 Licensed-Host Evidence Runbook

This runbook describes how an authorized Windows/CS2 host can produce the
external evidence required by `wp01-evidence.template.json`. It does not grant
license access and it cannot be satisfied by the public macOS checkout alone.

## Preconditions

- Use a dedicated Windows host with a valid game license and the authorized
  managed-assembly/mod loader version recorded in the evidence manifest.
- Clone the exact successor head under test; record `git rev-parse HEAD` before
  building. The manifest subject commit must equal that checkout's `HEAD`.
- Install the pinned toolchains listed by the selected successor PR. Record
  installer/source URLs as metadata, but hash the local installers and outputs.
- Keep secrets, license tokens, and personal identifiers out of artifacts.

## Required evidence sequence

1. **Public audit build**: run the successor's documented public-audit command;
   retain exit status, stdout, stderr, and produced binaries.
2. **Baseline tests**: run the complete permitted test command set on the same
   commit; retain machine-readable results and logs.
3. **Licensed adapter build**: build the adapter against the recorded game and
   managed-assembly versions; retain compiler output, binary, source revision,
   and dependency/toolchain versions.
4. **Launch smoke**: launch the licensed host with the adapter, exercise the
   minimum attach/handshake/projection path, and capture a bounded timestamped
   log. A launch that only compiles is not smoke evidence.
5. **Artifact provenance**: compute lowercase SHA-256 (and any policy-required
   additional digest) over every retained output; record exact relative paths,
   byte sizes, producing command IDs, and the subject commit.
6. **AgilePlus evidence record**: submit the evidence through a supported
   AgilePlus API/CLI operation. Record the feature slug, WP ID, resulting event
   or record ID, and hash of the submitted evidence. A handwritten SQLite edit
   is not acceptable.

## Manifest and acceptance

Populate the six required evidence IDs in the template, link each to command
and artifact IDs, and run:

```text
python3 scripts/verify_wp01_evidence.py REPO civic-wp01-evidence-v1.json
```

The verifier must run against the exact checkout named by `subject.commit` and
return `0`. A `1` result means evidence is pending/invalid; a `2` result means
the invocation or manifest is malformed. Preserve the raw manifest, logs, and
verifier output as immutable evidence. Do not overwrite an earlier bundle.

The final `GO` decision still requires independent review approval and the
program-specific conditional go/no-go record. Until then, keep WP01 `pending`
and do not begin WP02/native or production warfare implementation.
