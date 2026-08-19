# Registry Transaction and Failure Contract

The required ordering is:

`Manifest complete → register begins → Registry-local READ COMMITTED transaction → COMMIT → return to Universal Ingestion`

Only after commit may Event Engine processing begin. No Registry transaction may
span Event Engine execution, and no distributed or cross-component transaction is
authorized.

`PostgresRegistry.register(...)` is invoked exactly once by Universal Ingestion
after successful Manifest completion for the focused registered lifecycle.

On bounded `RegistryPersistenceError`:

- registration is unsuccessful;
- no EventEnvelope is constructed for publication;
- Event Engine receives zero calls;
- original, metadata, and Manifest remain intact;
- no retry or compensation occurs.

Unexpected Registry exceptions retain the existing propagation contract.
