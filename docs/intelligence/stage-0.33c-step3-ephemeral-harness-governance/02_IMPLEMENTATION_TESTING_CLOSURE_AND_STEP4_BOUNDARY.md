# Stage 0.33C-P3 Implementation, Testing, Closure, and Step-4 Boundary

## Future implementation allowlist

Only a future separately authorized and reviewed implementation may create at
most these four new files:

| Exact path | Purpose |
|---|---|
| `core/app/material_receipts/stage033c_one_shot_harness.py` | One-shot parser, exact DTO construction, invocation gate, controlled call, and bounded observable-result mapping |
| `tests/unit/app/material_receipts/test_stage033c_one_shot_harness.py` | Contract, one-shot, safety, and static-registration tests using fakes |
| `tests/integration/app/material_receipts/test_stage033c_one_shot_harness_no_write.py` | Optional isolated/no-write integration validation only |
| `docs/intelligence/stage-0.33c-step3-ephemeral-harness-implementation/00_IMPLEMENTATION_AND_VALIDATION_EVIDENCE.md` | Changed-file identity, hashes, tests, and zero-production-contact evidence |

The integration file is optional. No existing controlled entrypoint,
authorization, return type, repository, composition, adapter, configuration,
packaging, deployment, or service file may change. If DTO construction or
required evidence needs an interface change, implementation must stop for
separate architecture/interface governance. The harness has no direct DB,
repository, SQL, authorization-helper, authorization-file, or consumed-marker
access; it calls only the controlled entrypoint.

## Required input and one-shot tests

Tests must prove:

1. only the three top-level keys and exact nested fields frozen in the contract
   are accepted; every missing, duplicate, or unknown key is rejected;
2. `metadata` accepts only `{}`, `text` only `""`, `stored_path` only null, and
   raw image/PDF/DOC/DOCX/audio/voice/video/spreadsheet bytes, base64 content,
   binary blobs, retained payloads, free text, extension maps, and arbitrary
   per-item metadata are rejected;
3. every string/date/UUID/decimal bound, the 1–500 item bound, scalar bound,
   packaging formula, enum vocabulary, and state relationship is enforced;
4. the exact 4,255,678-byte transport maximum (4,255,677 semantic bytes plus
   one LF), canonical UTF-8 reserialization,
   semantic hash excluding LF, exactly one transport LF, and expected SHA-256
   match are enforced below, at, and above the bound;
5. exact `IngestionResult`, `TrustedReceiptFacts`, and
   `ControlledCandidateCreateRequest` construction has no actor, status,
   connection, credential, authorization, repository, or content injection;
6. invalid input causes zero calls, the gate transitions `UNUSED -> CLAIMED` at
   most once, a second attempt is rejected before the callable, and failure
   never enables retry; and
7. no loop, batch, fallback, daemonization, persistence, or resident worker
   behavior exists.

## Required result, error, and adversarial tests

Tests must prove the exact observable-only result schema and prove that
correlation/consumption/path state, actor claims, transaction internals, DB
details, row effects, and internal evidence events are absent. Result bytes are
canonical; stdout is one complete JSON object plus LF and <=4096 bytes;
serialization completes in a bounded buffer before one write; stderr is empty
for governed outcomes; and catastrophic stderr is the fixed <=42-byte line.

Every source maps to exactly one disjoint code 0, 10, 20, 30, 40, 50, 60, or 70
using exact exception type and bounded code, never message text. Tests exhaust
all 8 `CandidateCreateControlFailureCode`, all 7 `CandidateInputFailureCode`,
and all 9 `ReviewFailureCode` values frozen in document 01. They prove the
specific-code/type/fallback precedence, authorization activation -> 10,
consumed -> 20, invalid state -> 30, schema/DTO/candidate-input -> 40, every
current `ReviewApplicationError` code -> 50, authorization or harness output
durability -> 60, and only unclassifiable exceptions -> 70. Oversized result
finalization becomes a fixed bounded code-60 result; no partial JSON is emitted.

Decimal tests cover each named field independently and jointly: JSON strings
only; exact grammar; finite/range/precision/scale checks; no exponent, leading
plus/zero, trailing fractional zero, rounding, or quantization; negative and
zero rules; null/count relationship; packaging formula; integral `sheet`; the
48-character jointly valid per-item numeric maximum; and the exact quoted
lengths 15, 18, and 18 bytes. Size tests reproduce every row of document 01,
including unique line-number digits and direct four-byte UTF-8 scalar emission
without impossible control-character escape inflation.

For every governed and unexpected-exception path, adversarial values include:

- a very large exception message;
- embedded quotes, newlines, CRLF, tabs, and control characters;
- multibyte Unicode;
- an unexpected exception object;
- `password=`, `postgresql://`, `Bearer`, `sk-`, `token=`, and `PRIVATE KEY`;
- authorization-like JSON; and
- path-traversal-like strings.

Assertions show stdout remains valid canonical JSON and <=4096 bytes, stderr
obeys its empty/fixed-line contract, no traceback or exception repr is emitted,
and no secret-looking or user-controlled source value is reflected. Errors
contain only a closed-vocabulary classification and fixed safe message.

Tests also prove no direct SQL/repository/DB/authorization/marker access and no
HTTP, Telegram, systemd, cron, scheduler, agent/tool registry, background
worker, Universal Ingestion, CLI installation, or console-script registration.
Repository commit, harness SHA-256, Python identity/path/version, input SHA-256,
externally hashed bounded result, and callable symbol are available to later
supervisor evidence without claiming authorization-evidence completeness.

Mocks and fakes are the default. Optional DB coverage may use only isolated
PostgreSQL 17 with isolated credentials/data and no production route. No
production PostgreSQL, artifact, marker, candidate, real business input,
production-state callable invocation, or traffic mutation is allowed.

## Harness result and later evidence separation

The Step 3 result is limited to directly observable `ReceiptForReview` safe
fields plus deterministic harness-local fields. Later governance may combine it
with separately sourced authorization metadata, marker evidence, bounded
DB-side verification, and supervisor facts. That later evidence does not expand
the schema or authorize an interface change.

## Step 3 closure and Step-4 boundary

Step 3 does not close with this documentation. It may close only after a future
authorized implementation is independently reviewed and proves all frozen
contracts, including exact path, maximum four-new-file allowlist, one-process
at-most-one-call semantics, disjoint exits, output/secret safety, no direct
bypass, no permanent registration, and no production invocation.

The sequence remains:

1. Runtime prerequisites — `CLOSED / VERIFIED`.
2. Filesystem prerequisites — `CLOSED / VERIFIED`.
3. Ephemeral one-shot harness — governance remediation only; implementation and
   closure remain future work.
4. Real retained evidence plus trusted facts — **NOT AUTHORIZED**.
5. First-write authority.
6. Independent review and merge of that authority.
7. Exactly one bounded production write.

No step may be skipped, reordered, or collapsed. This package does not select
real values, begin Step 4, implement/invoke the harness, create
`authorization.json`, contact production PostgreSQL, invoke production
candidate creation, activate a candidate, merge PR #272, or authorize them.

Production PostgreSQL contacted: `NO`.

Harness implemented or invoked: `NO`.

`authorization.json` created: `NO`.

Candidate created or activated: `NO`.

Step 4 authorized or started: `NO`.

The next official action is fresh independent review of remediated PR #272. Do
not merge it as part of this remediation.
