# Failure and Preservation Evidence

Only `RegistryPersistenceError` is translated into
`registration_succeeded=False` and `registry_record_id=None`. Unexpected
exceptions remain visible.

Controlled post-Manifest persistence failure verified exactly one call, no
retry, no false success, and preservation of the stored original, metadata,
completed Manifest path, and Manifest artifact. No upstream deletion, rewrite,
relocation, rerun, or cross-component rollback occurs.
