# Registration Success Evidence

Successful Register returns a bounded ingestion result with
`registration_succeeded=True` and `registry_record_id` equal to the
committed database-local row ID.

All prior ingestion result information remains present. The complete
`RegistryPersistenceRow` does not cross as the lifecycle result, and the row
ID gains no canonical or domain meaning.
