# Stage 0.33C-P3 Harness Scope, Architecture, and Identity

## Authority and source gate

This documentation-only package records Project Owner approval to publish Step
3 governance and nothing else. Its source gate was clean at `HEAD == main ==
origin/main == 616e65894fd1d08e08fd3750b5f1691b88268142`. Step 1 and
Step 2 are `CLOSED / VERIFIED`; PR #271 is `MERGED / VERIFIED`; Step 3 is
current; Step 4 is not authorized.

This publication does not implement or invoke a harness, select input, create
`authorization.json`, create first-write authority, contact PostgreSQL, create a
candidate, or activate traffic.

## Frozen architecture

The future caller is one ephemeral Python process with at most one invocation
of the controlled callable. It is non-daemon, non-service, and not permanently
installed as a CLI. It is not an HTTP or Telegram adapter, cron job, scheduler,
agent, tool registration, background worker, or Universal Ingestion callback.
It has no resident state, polling, loop, retry, batch, fallback, or second-input
surface. After one bounded result or failure it exits.

The exact future source path is:

`core/app/material_receipts/stage033c_one_shot_harness.py`

It may be executed only from a separately reviewed immutable checkout as:

```text
/opt/aios/runtime/venv/bin/python -m core.app.material_receipts.stage033c_one_shot_harness --input-envelope <ABSOLUTE_PATH> --expected-input-sha256 <LOWERCASE_SHA256>
```

This command shape is an ephemeral module invocation, not a registered console
script. The two placeholders freeze the interface without selecting values.
The input path and digest must later be bound by separate governance; interactive
stdin, inline JSON, environment-selected input, and additional arguments are
prohibited.

## Runtime and source identity

Future execution must use Unix identity `aiosadmin:aiosadmin`; root execution
and sudo inside or around the harness are prohibited. The exact interpreter is
`/opt/aios/runtime/venv/bin/python`, and both runtime source/import root and
working directory are `/opt/aios-src`. Before execution, governance must bind
and verify the exact reviewed repository commit and require a clean,
Stage-0.33C-compatible checkout.

The harness imports the application capability only through
`core.app.material_receipts.controlled_candidate_create` and calls only
`controlled_create_review_candidate`. Imports needed solely to reconstruct the
exact governed DTO value types and bounded error enums are not alternate
application capabilities. Direct repository construction, direct SQL,
connection injection, authorization-function invocation, or calls to
`create_review_candidate_from_ingestion` are prohibited.

The request is exactly `ControlledCandidateCreateRequest` with its two frozen
fields: an exact `IngestionResult` and an exact `TrustedReceiptFacts`. Actor
reference, candidate status, DB connection, credential, authorization data,
retry policy, and repository are not request fields and cannot be supplied by
the harness.

## Authorization, credential, and marker boundary

The harness never creates, installs, edits, removes, chmods, or chowns
`authorization.json`. It relies only on the merged Stage 0.33C callable's fixed
authorization boundary. When authorization is absent or invalid, the controlled
call must fail closed before repository/DB capability. Installation remains a
later first-write-authority action.

The future artifact remains `root:aiosadmin`, `0440`, so `aiosadmin` can rely on
the merged reader without elevated execution. The harness must not touch the
`consumed` directory or create/read consumption markers directly; only the
merged authorization implementation owns marker state.

The existing governed environment mechanism may make
`AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD` available to the repository layer.
The harness must not read, copy, print, accept, serialize, hash, or persist that
value. It must not inspect `runtime.env` or dump its environment.

## No permanent registration

Implementation review must statically prove no registration or reference is
added to `setup.py`, `setup.cfg`, `pyproject.toml` entrypoints, systemd, cron,
Telegram, HTTP routing, schedulers, agent/tool registries, background workers,
or Universal Ingestion. No production installation path such as
`/usr/local/bin` is permitted.
