# Registration Failure Result

Universal Ingestion catches only `RegistryPersistenceError` from its single
Register call and returns the same bounded `IngestionResult` information with:

- `registration_succeeded = False`;
- `registry_record_id = None`.

No new error field or global error taxonomy is approved. The already-produced
stored path, metadata, completed Manifest path, input values, and existing
bounded dispositions remain available unchanged. The result must not report a
successful registration.

Failure causes no retry, second call, Storage/Metadata/Manifest rollback,
deletion, rewrite, or distributed transaction. Non-Registry programming and
contract errors are not silently translated by this rule.
