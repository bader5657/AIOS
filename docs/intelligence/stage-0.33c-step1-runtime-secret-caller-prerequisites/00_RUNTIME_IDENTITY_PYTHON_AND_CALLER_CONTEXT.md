# Stage 0.33C-P1 Runtime Identity, Python, and Caller Context

## Scope and source gate

This is Step 1 only. It does not begin filesystem provisioning, harness
creation, real-input selection, authority publication, or production writing.
The reviewed source gate was `HEAD == main == origin/main ==
3ad3d9d30dbdd0c8be42251051789cf3a96953e4`, with a clean worktree. Stage 0.33C
implementation remains CLOSED / VERIFIED and PR #264 remains MERGED / VERIFIED.

## Service identity evidence

Bounded installed metadata for `aios.service` establishes:

| Property | Value |
|---|---|
| `User=` | `aiosadmin` |
| `Group=` | `aiosadmin` |
| `WorkingDirectory=` | `/opt/aios-src` |
| `ExecStart=` | `/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main` |
| `EnvironmentFile=` | `/opt/aios/runtime/config/runtime.env` |
| `ActiveState=` | `active` |
| Main PID/start metadata | Present in bounded service metadata; not altered |

The future controlled caller must run as exactly `aiosadmin:aiosadmin`; this is
from service configuration, not interactive-shell identity. Root or sudo is not
required for application invocation.

## Python and import context

The installed interpreter is `/opt/aios/runtime/venv/bin/python`, Python 3.12.3.
The configured service repository is `/opt/aios-src`, but its current detached
checkout is `2c44dc84cb38dc51778f8a65f12a6e59683c74c9` and lacks
`core/app/material_receipts/controlled_candidate_create.py`; importing the
controlled module there fails. The reviewed source repository is
`/home/aiosadmin/AIOS` at the governed `main` commit and imports successfully
with that directory as the import root.

This is a caller-runtime prerequisite, not a reason to modify application code
in Step 1. Before Step 2, a separately governed deployment synchronization must
make the reviewed implementation available at the intended runtime import root,
or an equivalently reviewed immutable checkout must be selected. No code,
deployment tree, or service configuration was changed here.

## Controlled callable contract

The callable is imported as
`core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate`.
It is asynchronous and accepts exactly one
`ControlledCandidateCreateRequest(ingestion_result, trusted_receipt_facts)`.
The two values must be exact `IngestionResult` and `TrustedReceiptFacts`
instances; facts are validated before authorization. The callable returns the
existing `ReceiptForReview` or a bounded authorization/application error.

Authorization validates the fixed artifact, retained manifest and trusted-facts
binding, then claims once with `O_EXCL | O_NOFOLLOW` before the existing
`create_review_candidate_from_ingestion` path constructs
`MaterialReceiptRepository.from_environment()`. Evidence is a separate bounded
sink contract; the request contains no actor, credential, status override, path,
SQL, or retry input.

## Future caller boundary

The Step 3 caller must be an ephemeral one-process, one-invocation Python
execution under `aiosadmin`, using the reviewed interpreter and immutable source
root. It must terminate after one bounded result and must not be a daemon,
permanent CLI, HTTP route, Telegram handler, scheduler, agent, background worker,
or Universal Ingestion trigger. No such harness exists or was created in Step 1.
