# Lifecycle and Invocation Contract

The only approved sequence is:

```text
Recognition
  → Request Context
  → Asset Pipeline
  → Store Original where applicable
  → Extract Metadata
  → Create Document Manifest
  → Register handoff readiness
  → Universal Ingestion constructs RegistryPersistenceInput
  → PostgresRegistry.register(...)
  → bounded final ingestion result
```

Register may be called only when `pipeline_result.manifest_path` is a non-empty
completed-Manifest reference and `pipeline_result.register_handoff_ready` is
`True`. Existing Pipeline construction makes readiness true only when a
non-`None` Manifest path exists. Future integration must additionally reject
an empty path rather than pass it to Registry.

Storage, Metadata, or Manifest failure produces zero Registry calls. One
successful lifecycle reaching readiness produces exactly one call. No adapter,
fallback, retry, Pipeline, or Manifest call is permitted.
