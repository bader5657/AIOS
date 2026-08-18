# Registration Success Result

The existing `IngestionResult` may be minimally extended in
`core/ingestion/universal_ingestion.py` with exactly:

- `registration_succeeded: bool`, false unless Register completed successfully;
- `registry_record_id: int | None`, set to the returned row’s `record_id` only
  after successful commit.

All existing result information remains present. The complete
`RegistryPersistenceRow` must not cross as the ingestion lifecycle result.
`registry_record_id` is database-local, non-canonical, and carries no domain or
business meaning. Existing downstream readiness booleans are not reinterpreted
as registration success.
