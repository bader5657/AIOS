# Failure, State, Transition, and Duplicate Disposition

## Failure Contract

- storage failure prevents metadata, Document Manifest, and downstream
  readiness;
- metadata failure prevents Document Manifest and downstream readiness;
- Document Manifest failure prevents downstream readiness;
- a failed operation can never produce or retain a success disposition;
- no valid-looking partial Document Manifest survives a failed creation;
- stored originals are not deleted, rewritten, or mutated by later failure;
- Register is never executed by Asset Pipeline; and
- existing exceptions/failure boundaries may propagate without being
  reinterpreted as success.

No retry, compensation, recovery, transaction, timeout, cleanup expansion,
idempotency, or persistence semantics are authorized.

## State and Transition Policy

No persistent Asset Pipeline state machine is authorized. The historical
states `RECEIVED`, `STORED`, `METADATA_EXTRACTED`, `MANIFEST_CREATED`,
`COMPLETED`, and `FAILED` have no active authority.

Only the bounded terminal execution dispositions `success` and `failure` are
authorized conceptually. They are non-canonical outcomes, not persisted states
or a new lifecycle model. Concrete enum, class, string, or storage
representation is deferred and not authorized by Stage 4.1.1.

## Duplicate Disposition

**DUPLICATE DETECTION AND HANDLING: NOT AUTHORIZED IN STAGE 4.1.1**

No deduplication key, comparison, idempotency behavior, merge, skip, overwrite,
retry, or duplicate state may be inferred from historical code or tests. Stage
4.3.1 may test duplicate behavior only if a later explicit authority decision
defines it.
