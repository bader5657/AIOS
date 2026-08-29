# Implementation Scope, Entrypoint, and Exact File Allowlist

## Authority and baseline

This package governs implementation only. It grants no implementation authority
until this package passes fresh independent review and is merged unchanged. It
never grants a production write or activation authority.

| Item | Frozen value |
|---|---|
| Source `main` | `31c0b69c2e47d54edb7ba45fecceec3183a9d668` |
| Stage 0.33B / actor-provenance gate | `CLOSED` / `CLOSED` |
| Stage 0.33C readiness | PR `#261`, merged and verified |
| Readiness result | `IMPLEMENTATION_WORK_REQUIRED_BEFORE_ACTIVATION` |
| Candidate activation | `NOT AUTHORIZED` |
| Synthetic production data | `NOT AUTHORIZED` |

## Repository-truth create path

The current path is exactly:

1. `core/app/material_receipts/create_from_ingestion.py` —
   `create_review_candidate_from_ingestion(IngestionResult,
   TrustedReceiptFacts, ActorContext | None) -> ReceiptForReview`;
2. `core/app/material_receipts/candidate_input.py` —
   `build_receipt_candidate_request(...) -> ReceiptCandidateRequest`;
3. `core/app/material_receipts/review_use_cases.py` —
   `ReviewFacade.create_candidate(...) -> ReceiptForReview`;
4. `core/app/material_receipts/composition.py` —
   `_CandidateReviewOperations.create_candidate(...) -> ReceiptForReview`; and
5. `core/material_receipts/repository.py` — private
   `MaterialReceiptRepository._create_receipt_candidate(...) ->
   ReceiptForReview`.

The repository opens one Psycopg connection and one transaction, explicitly
sets `READ COMMITTED`, inserts the receipt and its items, changes only those new
rows to `NEEDS_REVIEW`, reads the result, and commits or rolls back atomically.

The private repository seam remains private. The implementation shall add no
public repository create method, raw-actor persistence API, direct SQL, nested
transaction, alternate composition, or bypass around the existing governed
path.

## Frozen controlled entrypoint

The new internal/manual application boundary is:

```python
await controlled_create_review_candidate(
    request: ControlledCandidateCreateRequest,
) -> ReceiptForReview
```

It is created at:

`core/app/material_receipts/controlled_candidate_create.py`.

`ControlledCandidateCreateRequest` is an exact frozen dataclass containing only
an exact `IngestionResult` and exact `TrustedReceiptFacts`. It contains no actor,
credential, activation flag, status, SQL, arbitrary path, transport object, or
retry field. The output is the existing exact `ReceiptForReview`. Control-plane
failures use a new closed `CandidateCreateControlFailureCode` and
`CandidateCreateControlError`; governed mapper and review errors remain their
existing bounded types.

The callable reads the fixed authorization boundary described in document 01,
constructs the sole trusted `ActorContext`, and invokes
`create_review_candidate_from_ingestion` once. It is not exported from
`core.app.material_receipts.__init__`, registered as a service/handler/task, or
made reachable from HTTP, CLI, Telegram, Universal Ingestion, an agent, or a
background worker. A later execution package must separately govern an executor.

## Exact implementation allowlist

No wildcard or implied supporting file is authorized. Every path below is
`NEW / CREATE`; the implementation modifies **zero existing files**.

### A. Application/runtime entrypoint

| Path | Disposition | Narrow purpose |
|---|---|---|
| `core/app/material_receipts/controlled_candidate_create.py` | `NEW / CREATE` | Exact request DTO and single controlled callable; reuse the existing governed create path only. |

### B. Activation/configuration and evidence boundary

| Path | Disposition | Narrow purpose |
|---|---|---|
| `core/app/material_receipts/candidate_create_authorization.py` | `NEW / CREATE` | Validate the one fixed authorization artifact, activation state, identity, expiry, one-request limit, and source/facts bindings before operational capability. |
| `core/app/material_receipts/candidate_create_evidence.py` | `NEW / CREATE` | Emit bounded, secret-safe implementation/runtime semantic evidence through an injected durable sink contract; no production root creation or activation. |

### C. Tests

| Path | Disposition | Narrow purpose |
|---|---|---|
| `tests/unit/app/material_receipts/test_controlled_candidate_create.py` | `NEW / CREATE` | Entrypoint ordering, exact DTOs, actor propagation, zero capability, non-escalation, and deactivation. |
| `tests/unit/app/material_receipts/test_candidate_create_authorization.py` | `NEW / CREATE` | Fixed-path artifact identity, owner/mode/symlink/schema/hash/expiry/binding validation and fail-closed behavior. |
| `tests/unit/app/material_receipts/test_candidate_create_evidence.py` | `NEW / CREATE` | Bounded schema, durability contract, secret/payload exclusion, and failure-before-advance behavior. |
| `tests/integration/business_context/test_stage033c_controlled_candidate_create_postgres.py` | `NEW / CREATE` | Isolated PostgreSQL 17 atomic effects, privileges, duplicate/concurrency, rollback, and forbidden side effects. |

### D. Implementation record

| Path | Disposition | Narrow purpose |
|---|---|---|
| `docs/intelligence/stage-0.33c-candidate-create-implementation/00_IMPLEMENTATION_AND_VALIDATION_EVIDENCE.md` | `NEW / CREATE` | Exact changed-file and executable validation record; no production evidence or payload. |

The allowlist is exactly eight paths. If implementation needs any initializer,
existing application module, repository, migration, helper, fixture, service,
script, runtime configuration, or additional document, it must stop and return
to governance before that path changes.

## Prohibited paths and capability expansion

Explicitly prohibited are Migration 0001–0005; provenance schema; DB role/GRANT
migrations; Stage V/V2/0.33B evidence; `runtime.env`; systemd or Docker files;
Telegram; Universal Ingestion write wiring; confirmation/review lifecycle
services; posting; inventory movement; material-stock code; HTTP routes; CLI
scripts; background workers; agent registrations; seed data; and production
automation.

The implementation capability is exactly one candidate-create request. It does
not include bulk creation, retry, update, confirmation, approval, acceptance,
rejection, cancellation, posting, inventory movement, stock mutation, or events
that trigger those operations.

## Project Owner decision

The Project Owner approves only this narrow implementation contract after fresh
independent review and unchanged merge. Approval excludes implementation before
merge, production activation, real production writes, Telegram, confirmation,
posting, inventory movement, stock mutation, new privileges, or runtime changes.
