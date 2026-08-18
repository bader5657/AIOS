# Register Failure Matrix

A deterministic real PostgreSQL persistence failure must be induced without a
schema change. The approved method is a disposable connection DSN with
`default_transaction_read_only=on`, applied only to the isolated database.

The test must prove:

- register raises `RegistryPersistenceError`;
- no Registry row is partially committed;
- the complete Registry-local transaction rolls back;
- no retry occurs;
- a later independent Registry operation remains usable; and
- Storage originals and Manifest artifacts are untouched.

No temporary constraint, migration edit, or runtime monkeypatch is authorized
as the primary integration evidence.
