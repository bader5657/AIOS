# Manifest Role and Registry Mapping

A successfully completed Document Manifest contributes its path/reference to the
registration boundary. The reference is not promoted to canonical business or
domain identity and receives no deduplication meaning.

The authorized `RegistryPersistenceInput` mapping is exact:

- `identity_ref = pipeline_result.manifest_path`
- `manifest_ref = pipeline_result.manifest_path`
- `represented_media_type = recognized_input_type.value`
- `metadata = pipeline_result.metadata`, preserving the exact value
- `storage_path = pipeline_result.stored_path` when present
- `source_url = text` only for approved Web/YouTube Link input
- `relationships = []`
- `registration_status = None`

RequestContext Telegram identifiers are not direct Registry fields. No additional
Registry field or identity semantic is authorized. Metadata, storage reference,
and exact source URL retain their accepted upstream meanings.
