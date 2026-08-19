# Transaction, Retry, Compensation, and Idempotency Rules

## Transaction boundaries

- Storage is independent.
- Metadata is independent.
- Manifest uses only its existing local atomic-write contract.
- Registry owns one Registry-local SQL transaction.
- Event Engine executes only after Registry commit.
- AIOS Core executes only after successful Event Engine completion.
- No transaction spans components and no distributed rollback exists.

## Prohibited recovery semantics

`RETRY = NONE` for Storage, Registry, handlers, Event publication, Core Route,
reroute, acknowledgement, and backoff. There is no retry loop or retry counter.

`COMPENSATION = NONE`. There is no cross-component deletion, Registry reversal,
Event compensation, or rollback of completed upstream artifacts.

`DEDUPLICATION / IDEMPOTENCY = NONE`. There is no idempotency key, failure
ledger, processed-event cache, route ledger, or duplicate suppression.
