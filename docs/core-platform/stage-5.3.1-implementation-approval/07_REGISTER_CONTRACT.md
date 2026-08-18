# Register Contract

Approved async operation: `register(input) -> RegistryPersistenceRow`.

Input fields are exactly:

- required `identity_ref`;
- required `represented_media_type`;
- required `metadata`;
- required `relationships`;
- required `manifest_ref`;
- optional `registration_status`;
- optional `storage_path`; and
- optional `source_url`.

`record_id` is not input; PostgreSQL generates it. Original binary, wholesale
Request Context, business fields, duplicate semantics, upsert, and caller
integration are prohibited.

Success returns the complete persisted database-local row. Persistence errors
raise `RegistryPersistenceError`, a Registry-local exception defined in the
same runtime file with no global taxonomy effect.
