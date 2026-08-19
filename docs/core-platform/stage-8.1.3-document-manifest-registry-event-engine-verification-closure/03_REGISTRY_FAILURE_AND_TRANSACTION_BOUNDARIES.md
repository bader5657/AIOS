# Registry Failure and Transaction Boundaries

A real Registry persistence failure was produced using a Registry connection
scoped to a nonexistent disposable schema. The existing
`RegistryPersistenceError` contract remained unchanged.

Evidence proved:

- one Registry attempt and no Registry retry;
- zero EventEnvelope constructions;
- zero `EventEngine.process()` calls;
- unsuccessful registration under the existing bounded result semantics;
- the stored original remained byte-for-byte intact;
- metadata remained intact;
- the completed Manifest remained present and valid;
- no compensation or rollback of upstream artifacts; and
- no backoff, retry counter, or fallback.

Registry owns and ends its SQL transaction before returning to Universal
Ingestion. Event Engine processing occurs after that return and outside the
Registry transaction. Registry has no Event Engine dependency, Event Engine has
no Registry dependency, and no distributed or cross-component transaction was
introduced.
