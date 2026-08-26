# Errors, Security Tests, and Production Safety

## Bounded errors and evidence

The implementation must map failures to bounded reason codes:
`RECEIPT_NOT_FOUND`, `INVALID_RECEIPT_STATE`, `STALE_RECEIPT_VERSION`,
`RECEIPT_NOT_CONFIRMED`, `NO_POSTABLE_ITEMS`, `ITEM_NOT_CONFIRMED`,
`MATERIAL_UNRESOLVED`, `MATERIAL_NOT_FOUND`, `MATERIAL_INACTIVE`,
`UNIT_MISMATCH`, `PACKAGING_FORMULA_INVALID`, `DUPLICATE_POSTING`,
`CONFLICTING_POSTING`, `DATABASE_UNAVAILABLE`, and `DATA_INTEGRITY_ERROR`.
A narrow cancellation-transition reason may be added only when needed. Raw
Psycopg, SQL, constraint, or DSN details must not cross the application boundary.

`PostingResult` contains only receipt ID, version, actor reference, outcome,
idempotency outcome, posted timestamp, and immutable movement evidence tuples
containing movement ID, source receipt-item ID, material ID, delta, unit, and
before/after balances. Logs and results exclude credentials, SQL, DSNs, document
binaries, and unnecessary supplier content.

## Credential and Brain isolation

Candidate persistence obtains only the candidate runtime credential. Posting
persistence obtains only the posting runtime credential. Their clients or pools
remain separate. The material-stock reader stays separately read-only. Admin
role `aios`, Docker exec, and credentials in DTOs are prohibited for application
persistence.

Brain and inference receive only narrow DTOs or application operations. They
receive no credential, database handle, generic SQL capability, writer
repository surface, confirmation authority, or posting authority. Inference may
propose candidates only.

## Required verification

Candidate functional tests cover valid and multi-item creation, both frozen
packaging examples, formula mismatch, fractional sheets, invalid units,
duplicate lines, unresolved review state, exact active material and unit at
confirmation, stale versions, version increments, confirmation invalidation,
invalid transitions, retained item cancellation, exclusion of cancelled items,
and absence of a physical deletion path.

Posting tests cover single, multi-item, and same-material posting; exact movement
and final balances; deterministic ordering; rollback on a later failure; exact
retry; conflicting duplicate; unresolved, missing, inactive, or unit-mismatched
materials; stale/non-confirmed receipts; zero applicable items; cancelled-item
exclusion; immutable movements; and lifecycle updates only after all stock work
succeeds.

Security tests use disposable PostgreSQL 17 roles and production-equivalent
column grants. Candidate must be denied movement insert/update, stock update,
receipt/item delete, and unrelated mutation. Posting must be denied receipt
business rewrites, item material/quantity/packaging rewrites, movement
update/delete/truncate, immutable stock-field update, and unrelated mutation.
The reader must remain read-only.

Tests require a dedicated non-production database, apply the governed migrations
and grants, create disposable schemas/roles, and remove them afterward. They
must reject production endpoints or credentials. Production grants are never
modified for test setup.

## Explicit non-authority

This stage performs no application implementation and authorizes no production
database mutation, sample receipt, stock mutation, movement, writer-credential
test, runtime environment change, systemd/service activation, Telegram change,
OCR/Vision work, inference invocation, automatic confirmation, or posting.
