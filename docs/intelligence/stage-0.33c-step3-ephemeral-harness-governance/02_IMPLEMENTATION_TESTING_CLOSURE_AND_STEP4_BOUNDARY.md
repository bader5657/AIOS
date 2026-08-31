# Stage 0.33C-P3 Implementation, Testing, Closure, and Step-4 Boundary

## Future implementation allowlist

Only a future separately reviewed implementation PR may create these files:

| Exact path | Purpose |
|---|---|
| `core/app/material_receipts/stage033c_one_shot_harness.py` | One-shot parser, exact DTO construction, invocation gate, controlled call, and bounded result mapping |
| `tests/unit/app/material_receipts/test_stage033c_one_shot_harness.py` | Contract, one-shot, safety, and static-registration tests using fakes |
| `tests/integration/app/material_receipts/test_stage033c_one_shot_harness_no_write.py` | Optional isolated/no-write integration validation only |
| `docs/intelligence/stage-0.33c-step3-ephemeral-harness-implementation/00_IMPLEMENTATION_AND_VALIDATION_EVIDENCE.md` | Changed-file identity, hashes, test results, and zero-production-contact evidence |

The first, second, and evidence files are the minimal expected set; the
integration file is optional and may be omitted. No existing Stage 0.33C
controlled-entrypoint, authorization, repository, composition, adapter,
configuration, packaging, deployment, or service file may change. If an
existing-file change appears necessary, implementation must stop and return for
a fresh architecture/governance decision.

## Required test contract

Tests must prove:

1. exact closed-schema parsing, byte bound, canonical reserialization, and
   input-digest match;
2. exact construction of `IngestionResult`, `TrustedReceiptFacts`, and
   `ControlledCandidateCreateRequest`, with no actor, status, connection,
   credential, or repository injection;
3. zero calls on invalid input and authorization-absent rejection before any
   fake repository/DB capability;
4. exactly one controlled-call attempt, including when it fails, and an
   explicitly rejected second invocation;
5. no loop, retry, batch, fallback, daemonization, persistence, or resident
   worker behavior;
6. exact stdout schema, 4096-byte bound, canonical result hashing, empty stderr
   for governed outcomes, and fixed fallback stderr only for code `70`;
7. exhaustive exit-code and bounded-error mapping with no traceback, raw
   payload, authorization bytes, environment values, or secret leakage;
8. no direct SQL, repository construction, DB connection injection,
   authorization helper call, or consumed-marker manipulation;
9. static absence from packaging entrypoints, systemd, cron, HTTP, Telegram,
   scheduler, agent/tool registry, background worker, and Universal Ingestion;
10. exact source SHA-256, repository commit, interpreter identity, entrypoint
    symbol, input SHA-256, and result SHA-256 are exposed for later binding.

Mocks and fakes are the default. Validation must not invoke the production
callable against production state. If DB-backed coverage is genuinely required,
it may use isolated PostgreSQL 17 only, with isolated credentials and data and
no production network route. No production DB, authorization artifact, marker,
candidate, or traffic mutation is allowed.

## Step 3 closure conditions

Step 3 does not close with this governance publication. It may close only after
the future allowlisted implementation is independently reviewed and proves:

- the ephemeral harness exists at the exact path;
- one-process, at-most-one-invocation semantics;
- exact safe input/output/error/exit-code contracts;
- no secret leakage or permanent registration;
- no direct DB/repository/authorization/marker bypass;
- no production invocation;
- deterministic input/result hashing and exact source identity binding; and
- Step 4 remains unexecuted.

## Step-4 boundary and sequence

After a separate Step 3 implementation closure review and unchanged merge,
Step 4 may become eligible to select and approve real retained evidence and
trusted facts. This package does not select them and does not begin Step 4.

The seven-step sequence remains exact:

1. Runtime prerequisites — `CLOSED / VERIFIED`.
2. Filesystem prerequisites — `CLOSED / VERIFIED`.
3. Ephemeral one-shot harness — governance published here; implementation and
   closure remain future work.
4. Real retained evidence plus trusted facts.
5. First-write authority.
6. Independent review and merge of that authority.
7. Exactly one bounded production write.

No step may be skipped, reordered, or collapsed.

## Project Owner and production boundary

Project Owner approval covers only publication of this Step 3 governance. It
does not approve implementation, real input, `authorization.json`, first-write
authority, candidate execution, or traffic activation.

Production PostgreSQL contacted: `NO`.

Harness implemented or invoked: `NO`.

`authorization.json` created: `NO`.

Candidate created: `NO`.

Step 4 started: `NO`.

Candidate activation: `NO`.

The next official action is fresh independent review of this governance PR.
Only after unchanged merge may the narrow allowlisted harness implementation be
proposed; it is not authorized by publication alone.
