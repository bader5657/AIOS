# Stage 0.33C-P3I Harness Implementation and Validation Evidence

## Authority and bounded scope

This implementation is governed by merged PR #272 at merge commit
`21f0ae1cdefdd3dc06abd0018c91815b2bfd1f7a`. The implementation branch was
created from that exact clean `main`. It adds exactly three files: the harness,
one unit-test file, and this evidence document. No existing file is modified;
the optional isolated integration file was not needed.

The reviewed implementation history before this evidence-only correction
contains two commits on top of the governance merge:

| Commit fact | SHA |
|---|---|
| Initial implementation commit | `a0d210a1020c9ab5df6f3e00bc2aeb2fadc38c89` |
| Cancellation/atomic-claim remediation commit | `13a5edb71a68c3c480bc0dfe7d9fa1f75b678c33` |
| Reviewed implementation HEAD | `13a5edb71a68c3c480bc0dfe7d9fa1f75b678c33` |
| Reviewed implementation commit count | `2` |

The subsequent evidence-only correction commit cannot truthfully contain its
own identifier; the implementation PR and supervisor report record that final
PR HEAD after the correction is committed.

## Implementation identity

| Fact | Frozen value |
|---|---|
| Harness | `core/app/material_receipts/stage033c_one_shot_harness.py` |
| Unit tests | `tests/unit/app/material_receipts/test_stage033c_one_shot_harness.py` |
| Harness SHA-256 | `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad` |
| Unit-test SHA-256 | `da47bc9b9371c7b6f7188e0305aa890f10cadc52db809eb726c905d85542e5de` |
| Controlled callable | `core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate` |

Canonical input algorithm identity is UTF-8 JSON with sorted keys,
`ensure_ascii=False`, separators `,` and `:`, `allow_nan=False`, duplicate-key
rejection, byte equality against the canonical serialization, and SHA-256 over
semantic bytes without the required final LF. The semantic limit is 4,255,677
bytes and transport limit is 4,255,678 bytes.

Result canonicalization uses the same deterministic JSON settings, adds exactly
one LF, serializes fully in memory, enforces 4,096 bytes including LF, and makes
one stdout write. Governed stderr is empty. The catastrophic boundary writes
only `AIOS_STAGE_0_33C_HARNESS_BOUNDARY_FAILURE\n`, exactly 42 bytes.

## One-shot and mapping proof

The private process state starts `UNUSED` and changes irreversibly to `CLAIMED`
immediately before the sole controlled-call attempt. A process-local
`threading.Lock` protects only the check-and-claim critical section and is
released before the callable. Four contending thread callers produce exactly
one winner and three pre-call losers; a separately paused winner also rejects a
loser before completion. Invalid input makes zero calls. A failed or cancelled
winner remains `CLAIMED`, and a later attempt is rejected. There is no retry,
loop, daemon, batch, fallback invocation, or permanent registration.

All current callable codes are covered exactly once:

| Family | Count | Exit distribution |
|---|---:|---|
| `CandidateCreateControlFailureCode` | 8 | 10:2, 20:1, 30:5 |
| `CandidateInputFailureCode` | 7 | 40:7 |
| `ReviewFailureCode` | 9 | 40:6, 50:3 |
| **Total callable codes** | **24** | **10:2, 20:1, 30:5, 40:13, 50:3** |

Callable mappings to exits 60 and 70 are zero.
`AUTHORIZATION_DURABILITY_FAILED` maps to 30 and
`INVALID_REVIEW_REQUEST` maps to 40. Exit 60 is harness-local output/evidence
durability only. An `asyncio.CancelledError` or an `Exception` outside the
governed callable inventory is explicitly sanitized as the harness boundary
classification at exit 70; no exception message, representation, traceback,
input, or secret is reflected. `SystemExit` and `KeyboardInterrupt` are not
blanket-caught through `BaseException`.

## Validation evidence

The canonical runner was
`PYTHONPATH=. /tmp/aios-stage-0-31b-venv/bin/python -m pytest`.

| Validation | Result |
|---|---|
| Focused harness unit tests | `70 passed in 0.55s` |
| Material-receipt regression suite | `333 passed in 1.13s` |
| Full repository suite | `1462 passed, 116 skipped, 3 warnings, 793 subtests passed in 17.30s` |
| Static compile of harness and tests | PASS |
| `git diff --check` | PASS |
| Exact new-file scope | PASS: three allowlisted new files after this evidence file; no existing modifications |
| Direct DB/repository/SQL/authorization-marker bypass scan | PASS: zero harness-source matches |
| Permanent-registration scan | PASS: zero harness-source matches and no registration/deployment file changed |
| Secret-token scan of harness source | PASS: zero matches |

Focused tests prove closed schemas, duplicate-key/UTF-8/size/hash rejection,
canonical decimals without rounding, the jointly valid decimal witness,
atomic four-thread claiming, paused-winner rejection, irreversible failed-winner
state, explicit secret-safe `CancelledError` exit 70, all 24 error codes, fixed
exit 60 and 70 behavior, strict
observable result fields, one-write stdout, fixed catastrophic stderr, and
adversarial non-reflection for large messages, quotes, backslashes, LF/CRLF,
tabs, Unicode, controls, password/database/token/private-key markers,
authorization-like JSON, and path traversal.

## Safety and next boundary

Production PostgreSQL contacted: `NO`.

Production controlled callable invoked: `NO`.

`authorization.json` created or modified: `NO`.

Candidate created or activated: `NO`.

Harness installed or permanently registered: `NO`.

Step 4 authorized or started: `NO`.

The next action is fresh independent review of the implementation PR. This
evidence does not authorize merging that PR, production invocation, real
business input, or Step 4.
