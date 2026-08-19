# Manifest, Registry Mapping, and Commit Evidence

Focused test execution used the current Universal Ingestion, Asset Pipeline,
Document Manifest, and PostgreSQL Registry runtimes. It proved a completed
Manifest file existed with `manifest_status = "created"` before the Registry
boundary was entered. Registry was never called before completion and was
called exactly once on each successful registration path.

The observed `RegistryPersistenceInput` mapping was exact:

- `identity_ref = pipeline_result.manifest_path`
- `manifest_ref = pipeline_result.manifest_path`
- `represented_media_type = recognized_input_type.value`
- `metadata = pipeline_result.metadata`, preserving object identity at handoff
- `storage_path = pipeline_result.stored_path` when present
- `source_url = text` only for an approved Web/YouTube link, preserving exact text
- `relationships = []`
- `registration_status = None`

No Telegram RequestContext identifier or username was a direct Registry field,
and no additional persistence field was present.

The unchanged migration was applied to a unique schema in a disposable
PostgreSQL 17 container. Registry executed its real READ COMMITTED transaction.
After `register()` returned, a test-local asynchronous Event Engine handler
opened an independent PostgreSQL connection and observed the expected record
and exact metadata immediately when handler execution began. This is direct
commit-visibility evidence, not call-order inference: Registry COMMIT completed
before Event Engine handler processing.
