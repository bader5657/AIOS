# Stage 0.33C-P3C Step 3 Implementation Evidence Review

## Review authority and source identity

This package reconciles merged Step 3 governance PR #272 and merged Step 3
implementation PR #273. It is documentation-only. The reviewed repository
identity is:

| Identity | Verified value |
|---|---|
| Repository `HEAD`, `main`, `origin/main` | `0b589717b70a71235cc312a0a517e1991a0ca6cd` |
| PR #272 | merged and verified; Step 3 governance |
| PR #273 reviewed HEAD | `e504b64e58e5c14cbef749f54d0f0ead3a6440bb` |
| PR #273 merge commit | `0b589717b70a71235cc312a0a517e1991a0ca6cd` |
| Harness | `core/app/material_receipts/stage033c_one_shot_harness.py` |
| Harness SHA-256 | `b9fc9fb22724184696eabf02525bcc0a626bdff5ce3943ed31ba2e21130f5cad` |
| Governed Python | `/opt/aios/runtime/venv/bin/python` (`Python 3.12.3`) |
| Controlled callable | `core.app.material_receipts.controlled_candidate_create.controlled_create_review_candidate` |

PR #273 history is exact and contains no stale single-commit claim:

1. initial implementation: `a0d210a1020c9ab5df6f3e00bc2aeb2fadc38c89`;
2. cancellation/atomic-claim remediation: `13a5edb71a68c3c480bc0dfe7d9fa1f75b678c33`;
3. evidence-only correction: `e504b64e58e5c14cbef749f54d0f0ead3a6440bb`;
4. merge: `0b589717b70a71235cc312a0a517e1991a0ca6cd`.

The PR introduced exactly three governed files: harness source, unit tests, and
implementation evidence. It modified zero existing files and added no runtime
configuration, deployment, packaging, or registration path.

## One-shot, concurrency, and cancellation evidence

The merged harness starts process-local state at `UNUSED`. A process-local
`threading.Lock` protects only the state inspection and irreversible transition
to `CLAIMED`; the lock is released before the controlled callable is attempted.
State is never restored, including after known failure, unexpected exception,
cancellation, or output failure. There is no retry, loop, batch, daemon, or
fallback invocation.

Retained tests establish four real concurrent callers, exactly one winner,
three rejected losers, and exactly one controlled-call attempt. A paused winner
holds no claim lock while executing; a concurrent loser is rejected before the
callable. A failed winner remains `CLAIMED`, and a later caller cannot take over.

`asyncio.CancelledError` is caught explicitly, not through a blanket
`BaseException` handler. It maps at the unexpected harness boundary to exit 70
`HARNESS_INTERNAL_FAILURE`. Tests prove one call, bounded canonical output,
empty governed stderr, and no traceback, raw cancellation text, user-input echo,
or reflection of `password=`, `postgresql://`, `Bearer`, `sk-`, or `token=`.

## Input, result, and output evidence

The implementation enforces a closed schema, rejects unknown and duplicate
keys, requires `metadata == {}`, admits 1–500 items, bounds every string and
collection, and exposes no field for raw file bytes, base64 document content,
binary payloads, or arbitrary metadata.

The semantic maximum is 4,255,677 bytes. Transport is exactly the semantic JSON
plus one LF and is capped at 4,255,678 bytes. Canonical JSON is sorted, compact,
direct UTF-8 (`ensure_ascii=False`), and rejects NaN/Infinity. Input identity is
SHA-256 over canonical semantic JSON bytes without LF.

`qty_per_full_colly`, `partial_qty`, and `total_qty` use canonical decimal
strings and `Decimal` construction: no float conversion, exponent, leading-plus
or leading-zero ambiguity, trailing fractional zero, rounding, or quantization.
Precision, scale, range, null/count, integrality, and packaging relationships
remain governed.

Results contain only `ReceiptForReview`-observable facts and deterministic
harness-local identities. Authorization, database, transaction, repository,
hidden actor, row-effect, and internal evidence facts are absent. Stdout is one
fully serialized canonical JSON object plus LF, at most 4,096 bytes, written
once after size validation. Governed stderr is empty; the catastrophic boundary
is one fixed sanitized 42-byte line. No raw exception or traceback is emitted.

## Error inventory and validation results

All 24 current callable codes map exactly once: 8 control, 7 candidate-input,
and 9 review codes. Exit cardinality is 10:2, 20:1, 30:5, 40:13, and 50:3.
Callable mappings to 60 and 70 are zero. `AUTHORIZATION_DURABILITY_FAILED` maps
to 30; `INVALID_REVIEW_REQUEST` maps to 40. Exit 60 is harness-local
output/evidence durability only. Exit 70 is the unexpected harness boundary,
including targeted cancellation. Message-text, substring, regex, and repr-based
semantic mapping are prohibited and absent.

Final accepted evidence is:

| Validation | Accepted result |
|---|---|
| Focused harness tests | 70 passed |
| Material-receipt regression | 333 passed |
| Full suite | 1,462 passed; 116 skipped; 793 subtests passed; 3 warnings |
| Static compile | PASS |
| Diff check | PASS |
| Bounded secret scan | PASS |
| Direct DB/repository/SQL/marker bypass audit | PASS |
| Permanent-registration audit | PASS |

No production PostgreSQL was contacted, no production authorization artifact
was created, the harness was not invoked against production, and candidate
creation count is zero.
