# Candidate Activation Capability and Safety Boundary

## Exact current write path

The implemented candidate-create path is:

1. `core/app/material_receipts/create_from_ingestion.py` —
   `create_review_candidate_from_ingestion` captures and authorizes the actor,
   maps validated input, and exposes only the create capability.
2. `core/app/material_receipts/candidate_input.py` —
   `build_receipt_candidate_request` validates retained ingestion evidence and
   trusted facts and creates immutable UUIDv4 request identities.
3. `core/app/material_receipts/review_use_cases.py` —
   `ReviewFacade.create_candidate` checks source identity and retained evidence.
4. `core/app/material_receipts/composition.py` —
   `_CandidateReviewOperations.create_candidate` is the transient service and
   repository boundary.
5. `core/material_receipts/repository.py` —
   private seam `MaterialReceiptRepository._create_receipt_candidate` creates
   one Psycopg connection and one `READ COMMITTED` transaction.

The application/runtime role is
`aios_material_receipt_candidate_runtime`; its governed PostgreSQL membership is
`aios_material_receipt_candidate_writer`. Configuration is loaded only by
`CandidateDatabaseConfig`/`MaterialReceiptRepository.from_environment`, using
`AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`, database `aios`, host
`127.0.0.1`, port `5432`, and TLS disabled.

Candidate creation inserts one `material_receipts` row and one or more
`material_receipt_items` rows, then changes those new rows to `NEEDS_REVIEW`
inside the same transaction. It does not confirm, post, create
`inventory_movements`, or mutate `material_stock`.

## Actor and privilege boundary

`core/app/material_receipts/actor_provenance.py` accepts only
`operator:<canonical-lowercase-UUIDv4>`. The public boundary revalidates the
`ActorContext`, captures the canonical string once, drops the context reference,
and passes no raw public actor argument to the private persistence seam. This
preserves Actor A and supplies no Actor B impersonation mechanism.

Creation writes `created_by_actor_reference` once. The verified privilege
baseline remains: candidate creator INSERT is governed; candidate creator
UPDATE is absent; posting creator UPDATE is absent; reader write is absent;
R03/R04/V05 are PASS. No privilege broadening is required or proposed.

## Exact input contract

The source must be an exact `IngestionResult` whose retained manifest is a
regular, non-symlink canonical manifest with matching UUID identity. Registration
and handoff flags must satisfy the mapper contract, and `brain_result` must be
absent. The source manifest reference supplies source identity and is protected
by the verified active-source unique partial index. A concurrent or repeated
active source maps to `SOURCE_ACTIVE_RECEIPT_EXISTS`; it is not normalized into
a second candidate.

Trusted receipt facts require:

- canonical nonblank supplier name (maximum 128 characters);
- optional canonical document number (maximum 128) and optional document date;
- timezone-aware received timestamp;
- 1–500 uniquely numbered items;
- per-item optional canonical description/display/size/specification fields,
  each at most 512 characters, and optional UUID material identity;
- nonnegative bounded packaging values, positive bounded total quantity, scale
  at most 6, precision at most 20, and exact packaging formula equality; and
- unit exactly one of `sheet`, `pcs`, `kg`, `roll`, or `pack`, with integral
  sheet quantities.

Receipt and item identifiers are fresh distinct UUIDv4 values. A valid candidate
returns only `NEEDS_REVIEW`, with no confirmation version, timestamp, or actor.

Technical input validity does not establish business-data eligibility. No
synthetic production candidate is allowed by this package. The first real
candidate requires Project Owner approval of the exact retained source and
business facts; this package invents no data.

## Current activation state and unintended seams

Production candidate activation is both **governance-disabled** and
**runtime-disconnected**:

- the actor-provenance gate is closed, but runtime-secret/activation safety and
  explicit production safety review remain open;
- there is no production call site for
  `create_review_candidate_from_ingestion` outside its export/definition;
- `core/adapters/telegram/main.py` stops after Universal Ingestion and an
  acknowledgement and does not construct trusted receipt facts or candidate
  actor identity;
- `core/ingestion/universal_ingestion.py` returns ingestion evidence and does
  not call candidate creation;
- no HTTP route, background task, or automatic agent path calls the capability;
  and
- no governed operator/manual activation entrypoint exists.

The Python function is importable internal application code, so it becomes
operational only if a future caller deliberately supplies valid retained
evidence, trusted facts, an authorized actor, and the candidate credential. No
currently wired production path does so. No unexpected active production write
seam was found by static call-site review; none was exercised.

Telegram and Universal Ingestion are outside the immediate activation scope.
Telegram lacks the separately governed sender-to-canonical-operator binding and
would broaden the trust surface. Universal Ingestion must continue producing
evidence only during the first activation. Automatic agent writes are likewise
deferred.

## Zero-operational-capability requirement

Existing unit and disposable-integration tests cover fail-closed input mapping,
actor rejection, repository/credential/connection non-use for rejected input,
duplicate/concurrent source handling, and non-escalation into confirmation or
posting. Before activation, Stage 0.33C implementation must turn this principle
into a deterministic activation-entrypoint proof: every invalid, incomplete,
unauthorized, duplicate, or ineligible request must fail before repository
construction, credential loading, database connection, persistence,
confirmation, posting, inventory movement, or stock mutation.
