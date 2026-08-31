# Stage 0.33C-P3I Harness Implementation and Validation Evidence

## Authority and bounded scope

This implementation is governed by merged PR #272 at merge commit
`21f0ae1cdefdd3dc06abd0018c91815b2bfd1f7a`. The implementation branch was
created from that exact clean `main`. It adds exactly three files: the harness,
one unit-test file, and this evidence document. No existing file is modified;
the optional isolated integration file was not needed.

The implementation commit candidate is the single commit containing this
three-new-file diff on top of the governance merge. Its final SHA is recorded
by the implementation PR and supervisor report after the commit is created; a
commit cannot truthfully contain its own identifier.

## Implementation identity

| Fact | Frozen value |
|---|---|
| Harness | `core/app/material_receipts/stage033c_one_shot_harness.py` |
| Unit tests | `tests/unit/app/material_receipts/test_stage033c_one_shot_harness.py` |
| Harness SHA-256 | `9e78222b3f8611f40b9440b2b91a9f9bc7c4e3e3c5ef424b37c42c414623f427` |
| Unit-test SHA-256 | `a1a041874265959f3d98762750567949aa50d7f6a3cbf4fc6aef7602f9349419` |
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
immediately before the sole controlled-call attempt. Invalid input makes zero
calls. A second attempt after claim is rejected before invocation. There is no
retry, loop, daemon, batch, fallback invocation, or permanent registration.

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
durability only. An exception outside the governed callable inventory is
sanitized as the harness boundary classification at exit 70; no exception
message, representation, traceback, input, or secret is reflected.

## Validation evidence

The canonical runner was
`PYTHONPATH=. /tmp/aios-stage-0-31b-venv/bin/python -m pytest`.

| Validation | Result |
|---|---|
| Focused harness unit tests | `66 passed in 1.41s` |
| Material-receipt regression suite | `329 passed in 1.49s` |
| Full repository suite | `1458 passed, 116 skipped, 3 warnings, 793 subtests passed in 16.53s` |
| Static compile of harness and tests | PASS |
| `git diff --check` | PASS |
| Exact new-file scope | PASS: three allowlisted new files after this evidence file; no existing modifications |
| Direct DB/repository/SQL/authorization-marker bypass scan | PASS: zero harness-source matches |
| Permanent-registration scan | PASS: zero harness-source matches and no registration/deployment file changed |
| Secret-token scan of harness source | PASS: zero matches |

Focused tests prove closed schemas, duplicate-key/UTF-8/size/hash rejection,
canonical decimals without rounding, the jointly valid decimal witness,
one-shot call count, all 24 error codes, fixed exit 60 and 70 behavior, strict
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
