# Test, Security, and Implementation Gates

## Mandatory future test policy

All requirements below are permanent and mandatory for a separately authorized implementation. They are not supplemental or implied proofs. No production PostgreSQL is required or authorized during Stage 0.33A implementation.

## Unit and application tests

Tests must prove:

- a valid `operator:<canonical-lowercase-uuidv4>` persists;
- generic `ActorContext` retains its existing broader grammar and unrelated consumers remain unaffected;
- candidate creation separately authorizes only the operator/canonical-lowercase-UUIDv4 form;
- a structurally valid `reviewer:<id>` is rejected for candidate creation as `ACTOR_UNAUTHORIZED`;
- malformed, noncanonical, or prohibited-shaped identity is rejected as `ACTOR_INVALID`, while a missing actor is `ACTOR_REQUIRED`;
- actor identity remains separate from `IngestionResult` and `TrustedReceiptFacts`;
- application validation rejects blank, unknown prefixes, uppercase or non-v4 UUIDs, alternate UUID forms, control characters, Unicode lookalikes, path-shaped, SQL-shaped, DSN-shaped, credential-shaped, and overlength values;
- no public raw string, dictionary, or JSON actor parameter is introduced; and
- invalid actor state fails before mapper, candidate capability, repository construction/calls where the governed design permits, database connection, or database mutation.

Expected zero-side-effect evidence is mapper calls `= 0`, candidate capability calls `= 0`, repository construction/calls `= 0` where the governed design permits, and database connections/mutations `= 0`.

## Forged-object tests

Every candidate-creation public boundary must revalidate the current `ActorContext` value. Construction-time validation is insufficient. Tests must reject:

- an `ActorContext` forged with `object.__new__`;
- mutation through `object.__setattr__` where technically possible;
- subclass substitution where exact-type policy applies;
- a manually reconstructed object;
- malformed deserialized state;
- a valid object mutated after initial construction; and
- unexpected attribute injection where the object model permits.

Each forged-object case must prove the same zero downstream activity required for invalid actors.

## Trust-boundary adversarial tests

Tests must prove that only a separately supplied, authenticated `ActorContext` from the trusted AIOS identity boundary provides creator authority. The following must not directly or indirectly become creator identity:

- Telegram text or caption containing `operator:<valid-uuidv4>`;
- Telegram sender `user_id` or arbitrary Telegram metadata;
- `IngestionResult` metadata or `TrustedReceiptFacts` fields;
- documents, supplier values, or document values;
- OCR, Vision, LLM, or Brain output;
- an arbitrary dictionary/JSON actor field; or
- database login username.

A Telegram sender-to-AIOS-identity resolver remains separately governed and unauthorized by this package.

## PostgreSQL migration and schema tests

Real disposable PostgreSQL must prove:

- Migration 0005 `UP` succeeds on the approved empty baseline;
- the column exists as exactly `TEXT NOT NULL`;
- the database `CHECK` exists and enforces the exact frozen semantics;
- no unapproved index exists;
- `DOWN` is tested only in disposable PostgreSQL;
- `UP → DOWN → UP` succeeds where lifecycle testing is appropriate; and
- schema and object preservation holds.

Actual PostgreSQL constraint tests must pass `operator:<valid-lowercase-canonical-uuidv4>` and reject:

- uppercase UUIDv4;
- UUIDv1, UUIDv3 where constructible, and UUIDv5;
- the zero UUID;
- malformed UUID, missing-hyphen, and braced UUID forms;
- leading or trailing whitespace;
- `reviewer:<valid-uuidv4>` and `system:<valid-uuidv4>`;
- blank text; and
- `NULL` under the `NOT NULL` constraint.

These tests prove database constraint behavior, not merely application validation.

## Privilege tests

Disposable PostgreSQL security tests must prove:

- candidate runtime can insert only the approved candidate-creation columns, including a valid `created_by_actor_reference`;
- candidate runtime cannot update, erase, or rewrite `created_by_actor_reference`;
- candidate runtime cannot perform generic provenance updates or unrelated provenance writes;
- candidate runtime has no posting, movement, stock, admin, ownership, DDL, or grant-option authority;
- posting runtime cannot update `created_by_actor_reference`; and
- no runtime identity can mutate original creator provenance after insertion.

## Atomicity tests

Tests must prove receipt header, receipt items, and creator provenance commit in the same existing transaction. A forced failure after receipt insertion or during item creation must leave:

```text
receipt committed = 0
items committed = 0
provenance committed = 0
```

No receipt may commit without required creator provenance.

## Stage 0.32 regression tests

Tests must prove:

- `created_by_actor_reference` is not a deduplication key;
- same source by a different actor returns `SOURCE_ACTIVE_RECEIPT_EXISTS`;
- no second active receipt is created and provenance is not mutated;
- the duplicate response does not disclose the original creator; and
- `material_receipts_source_asset_active_uidx`, its uniqueness, and its predicate remain exact and unchanged.

Migration 0004 must not be changed or rerun. Stage 0.32 remains closed.

## Lifecycle and immutability tests

Tests must prove revision, review, confirmation, rejection, cancellation, and posting preserve the original creator. A rejected or cancelled receipt retains its original actor, while a legitimate replacement receives a distinct, newly authenticated actor with no inheritance or copying.

## Schema and object preservation tests

Migration 0005 must be proven not to alter existing indexes, unrelated columns, triggers, functions, roles, ownership, unrelated ACLs, or business data. Preservation proof includes the Stage 0.32 index and behavior.

## Provenance non-exposure tests

Permanent tests must prove:

- duplicate responses do not contain the existing creator;
- Brain inputs and LLM prompts/context receive no creator reference;
- Telegram acknowledgements and replies do not echo the creator;
- Universal Ingestion results and metadata do not gain creator identity;
- generic logs and errors do not emit creator identity unexpectedly;
- generic object traversal exposes no repository, credential, or authentication internals; and
- no generic provenance-query API or unapproved repository getter is introduced.

## Exception-graph tests

Recursive failure-path review must cover actor-validation and database failures. Outward errors may expose only bounded actor failure codes and explicitly safe values. They must not expose credentials, DSNs, SQL, repository/configuration objects, authentication-resolver internals, Telegram identity-binding internals, database connections, traceback locals, or unsafe untrusted original actor strings.

## Production-preflight tests

Tests must prove the production preflight contract fails closed. The simple `NOT NULL`, no-backfill path is eligible only after a separately authorized immediate read-only production query returns scalar `0`:

```sql
SELECT COUNT(*)
FROM public.material_receipts;
```

A positive result must stop deployment with no alternate migration strategy, temporary nullable column, fabricated backfill, or invented provenance. Historical rows require separate governance.

## Security invariants

- Candidate creation revalidates generic `ActorContext` structure/trust, then applies the operation-specific authorization policy.
- Actor references are non-secret identity metadata and never carry credentials or secrets.
- Creator provenance is immutable and unavailable through generic update or read surfaces.
- Duplicate-source behavior neither changes provenance nor leaks the existing creator.
- Runtime privileges remain least-authority.
- Telegram, Universal Ingestion, OCR, Vision, LLM, and Brain gain neither actor authority nor automatic provenance exposure.

## Frozen stage sequence

### Stage 0.33A

```text
governance merge
→ separate implementation authority
→ implementation + Migration 0005 files
→ disposable PostgreSQL/security tests
→ independent implementation review
→ merge
```

The governance merge is not implementation authority. Migration files, application changes, role/grant changes, production operations, and the Telegram identity resolver require separate explicit authority.

### Stage 0.33B

```text
separate production read-only preflight
→ one-shot Migration 0005 deployment
→ post-deployment verification
→ actor-provenance operational gate closure
```

Migration 0005 deployment is contingent on the immediately preceding zero-row result and every applicable approval. A positive row count is a hard stop. Production `DOWN` is not authorized. Production activation remains outside Stage 0.33B until all other gates close.

## Remaining gates

These gates remain open:

- **RUNTIME-SECRET ROTATION / ACTIVATION SAFETY**
- **EXPLICIT PRODUCTION SAFETY REVIEW**

The actor-provenance operational gate is not closed during Stage 0.33A. Production candidate traffic remains **NOT AUTHORIZED**.

## Remediated classification

**STAGE 0.33A GOVERNANCE DECISION FROZEN**

**— READY FOR FRESH INDEPENDENT GOVERNANCE REVIEW**

**— IMPLEMENTATION NOT YET AUTHORIZED**

**— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED**
