# Read Failure Matrix

Required cases:

| Case | Expected result |
|---|---|
| Existing row | Complete persistence row |
| Missing `record_id` | `None`; not an error |
| True database read failure | `RegistryPersistenceError` |

The approved database-failure method is an isolated test connection scoped to
a disposable empty schema/search path where `registry_records` is absent.
This produces a real PostgreSQL undefined-table error without altering the
approved Registry schema.

Read failure must not mutate database state, retry, or affect Storage/Manifest.
