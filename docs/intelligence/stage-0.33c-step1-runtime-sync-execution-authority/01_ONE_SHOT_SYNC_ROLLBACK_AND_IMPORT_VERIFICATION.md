# One-Shot Synchronization, Rollback, and Verification

## Bounded rollback

Same-session rollback is authorized exactly once only when the exact checkout
mutation succeeded but post-sync identity or import verification fails. Rollback
may only detach the checkout to the recorded pre-sync SHA
`2c44dc84cb38dc51778f8a65f12a6e59683c74c9`. It is not a forward retry, does not
restore authority, and leaves Step 1 open. No arbitrary rollback target, reset of
unknown work, cleanup, deletion, or second forward attempt is permitted.

## Service boundary

`aios.service` restart, stop/start, kill, and relaunch are expressly prohibited
by this authority. Python modules are resident after process start; the dormant
Stage 0.33C callable is not part of the active Telegram entrypoint. The existing
service must retain its pre-sync active state, PID, and start identity. Any
unexpected service impact is a stop condition; a future technical need for a
restart requires `SEPARATE_RESTART_AUTHORITY_REQUIRED`.

## Non-write import verification

After successful checkout, from `/opt/aios-src`, use the existing runtime
interpreter and prevent bytecode writes:

```sh
cd /opt/aios-src
PYTHONDONTWRITEBYTECODE=1 /opt/aios/runtime/venv/bin/python -c '
import core.app.material_receipts.controlled_candidate_create as controlled
import core.app.material_receipts.candidate_create_authorization as authorization
import core.app.material_receipts.candidate_create_evidence as evidence
assert callable(controlled.controlled_create_review_candidate)
print(controlled.__file__)
print(authorization.__file__)
print(evidence.__file__)
'
test "$(git -C /opt/aios-src rev-parse HEAD)" = "964193f2e567b5109de50c427bbbf632b2198958"
test -z "$(git -C /opt/aios-src status --porcelain)"
```

This command must not invoke the callable, construct a request, initialize
`MaterialReceiptRepository.from_environment()`, read a credential, connect to
PostgreSQL, or write evidence. It proves all three modules and direct imports,
the callable assertion, exact SHA, and clean worktree. Any import, commit,
generated-file, or cleanliness failure stops execution and permits only the
explicit rollback.

## Health and secret checks

Capture service active state, PID, and `ExecMainStartTimestamp` before and after;
they must be unchanged. Confirm environment-file metadata only. Do not print or
inspect `runtime.env`, `AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`, database
URLs, tokens, or private keys. Production PostgreSQL contact and candidate writes
are zero.
