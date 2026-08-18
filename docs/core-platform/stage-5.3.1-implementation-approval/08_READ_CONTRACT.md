# Read Contract

Approved async operation:

`read(record_id) -> RegistryPersistenceRow | None`

The lookup key is database-local `record_id`, the only approved unique key.
Ordinary not-found returns `None`. Persistence errors raise the Registry-local
persistence error.

No identity/Manifest/path/URL/checksum lookup, list, search, filter, pagination,
query API, or lock is authorized.
