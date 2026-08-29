# Stage 0.33C Controlled Candidate-Create Implementation Evidence

## Authority and identity

| Item | Value |
|---|---|
| Governance PR | `#262` |
| Governance reviewed HEAD | `d9ee60fd8ba32944bd79c5419cb85cf0fd0aa9c7` |
| Governance merge/base commit | `1e2d571a0729b80a14d0b53ef0de34e7bae29e26` |
| Implementation branch | `impl/stage-0.33c-controlled-candidate-create` |
| Implementation commit | This record's enclosing PR HEAD, retained in immutable Git/PR metadata |
| Production activation | `NOT AUTHORIZED` |
| Production PostgreSQL contact | `NONE` |

The implementation creates exactly the eight paths authorized by PR #262 and
modifies zero existing files:

1. `core/app/material_receipts/controlled_candidate_create.py`
2. `core/app/material_receipts/candidate_create_authorization.py`
3. `core/app/material_receipts/candidate_create_evidence.py`
4. `tests/unit/app/material_receipts/test_controlled_candidate_create.py`
5. `tests/unit/app/material_receipts/test_candidate_create_authorization.py`
6. `tests/unit/app/material_receipts/test_candidate_create_evidence.py`
7. `tests/integration/business_context/test_stage033c_controlled_candidate_create_postgres.py`
8. `docs/intelligence/stage-0.33c-candidate-create-implementation/00_IMPLEMENTATION_AND_VALIDATION_EVIDENCE.md`

## Implemented boundary

The internal/manual entrypoint is exactly
`controlled_create_review_candidate(ControlledCandidateCreateRequest) ->
ReceiptForReview`. The frozen request contains only exact `IngestionResult` and
`TrustedReceiptFacts`. It accepts no actor, credential, status, SQL, path,
transport, or retry input. It is not exported or registered.

The fixed production authorization path and consumption directory are exactly:

- `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json`
- `/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed`

Production defaults fail closed. The implementation does not provision either
location. The artifact is bounded to 16 KiB, strict duplicate-rejecting UTF-8
JSON with a closed schema, exact `root:aiosadmin`/`0440` production metadata,
canonical lowercase UUIDv4 authorization and operator identities, canonical UTC
window, `max_requests` exact integer `1`, and exact raw-manifest/canonical-facts
SHA-256 bindings.

The sole claim is direct `os.open` with
`O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`, mode `0600`. Successful exclusive
creation is irreversible consumption. The winner writes bounded semantic JSON,
file-fsyncs, and parent-directory-fsyncs before returning DB capability. A
post-claim write or durability failure retains the marker and cannot restore
authority. A safe empty, partial, or unfsynced marker is `CONSUMED`; losers use
metadata only and never parse its body. Unsafe types or metadata return
`AUTHORIZATION_CONSUMPTION_STATE_INVALID` without repair, deletion, wait,
takeover, or retry.

After durable claim, the entrypoint derives the sole `ActorContext` from the
artifact and invokes the existing `create_review_candidate_from_ingestion` path
exactly once. Credentials remain exclusively behind existing
`MaterialReceiptRepository.from_environment()`. No confirmation, posting,
inventory, stock, Telegram, HTTP, CLI, scheduler, agent, or Universal Ingestion
write registration was added.

## Executed validation

All commands used `PYTHONPATH=.` and the pre-existing
`/tmp/aios-stage-0-31b-venv`; no dependency or repository configuration changed.

### Focused unit tests

```text
/tmp/aios-stage-0-31b-venv/bin/pytest -q
  tests/unit/app/material_receipts/test_candidate_create_authorization.py
  tests/unit/app/material_receipts/test_controlled_candidate_create.py
  tests/unit/app/material_receipts/test_candidate_create_evidence.py
```

Final result: `40 passed in 0.46s`.

The authorization tests include 25 simultaneous same-authorization callers:
one winner and 24 metadata-only `AUTHORIZATION_CONSUMED` losers. Empty and
partial marker tests prohibit body reads. File-fsync and parent-fsync failure
tests retain consumed state and reject the later caller. Entrypoint negative
tests prove the existing governed create function is called zero times for
pre-claim failure and exactly once after successful authorization/durability.

### Material-receipt regression tests

```text
/tmp/aios-stage-0-31b-venv/bin/pytest -q
  tests/unit/app/material_receipts tests/unit/material_receipts
```

Final result: `274 passed, 4 subtests passed in 1.03s`.

### Isolated PostgreSQL 17 integration

The admitted target was a dedicated ephemeral `postgres:17-alpine` container on
numeric loopback port `55445`, database
`aios_material_disposable_stage033c`, with explicit
`AIOS_MATERIAL_DISPOSABLE_TESTS=1`. Server version: `17.10`. It was not a
production endpoint and contained no production data or credential.

```text
/tmp/aios-stage-0-31b-venv/bin/pytest -q
  tests/integration/business_context/test_stage033c_controlled_candidate_create_postgres.py
```

Final result: `4 passed, 3 subtests passed in 1.18s`.

The integration results prove one receipt plus two linked items, all
`NEEDS_REVIEW`; the artifact-derived actor value at persistence; zero
confirmation, inventory movement, and stock effects; later-item failure rollback
to zero partial rows; bounded `SOURCE_ACTIVE_RECEIPT_EXISTS`; a real two-connection
source race with one success and one duplicate; exact candidate-writer ability;
and denial of candidate, inventory, and stock writes for a separate forbidden
role. Authorization contention is not reused for database contention.

### Full repository suite

```text
/tmp/aios-stage-0-31b-venv/bin/pytest -q tests
```

Final clean-container result: `1440 passed, 68 skipped, 830 subtests passed in
26.69s`, with three pre-existing pytest collection warnings.

An earlier broad attempt produced 41 cascading failures because the new
integration teardown initially retained the shared test candidate role. That
aborted older integration setup before its temporary manifest-root restoration.
The allowlisted new integration test was corrected to remove its test role, the
disposable container was recreated from scratch, and the complete clean rerun
above passed.

### Static and scope checks

- `python3 -B -m py_compile` over all seven new Python files: `PASS`.
- Direct imports of all three application modules: `PASS`.
- `git diff --check`: `PASS`.
- Changed-file allowlist: exactly eight governed new paths.
- Existing tracked files modified: zero.
- Registration scan across the three application modules for Telegram, HTTP,
  CLI, scheduler, background worker, agent, Universal Ingestion, handler, route,
  and task wiring: zero matches.
- Secret-surface scan for database URL, `runtime.env`, DB password, password,
  private/API keys, and token fields across the application modules: zero
  matches.

## Effects, evidence, and limitations

The existing repository continues to own one connection and one atomic
`READ COMMITTED` transaction. The governed successful effect is one receipt and
N items in `NEEDS_REVIEW`; confirmation, posting, inventory movement, and stock
effects remain zero. Duplicate handling remains
`SOURCE_ACTIVE_RECEIPT_EXISTS`, with no automatic retry or existing-candidate
success substitution.

The evidence module emits only bounded semantic identifiers, digests, claim and
durability outcomes, DB-capability attempted state, candidate/result identity,
row effects, zero non-escalation effects, and result classification through an
injected durable sink. It rejects non-governed status/effects and contains no
unrestricted business payload or secret.

No production authorization artifact, consumption directory/marker, evidence
root, executor, or production write authority was created. The controlled
callable remains disconnected. A separately governed first-write package must
provision and hash-bind all production artifacts and authorize exact real input.
Production candidate activation remains **NOT AUTHORIZED**.
