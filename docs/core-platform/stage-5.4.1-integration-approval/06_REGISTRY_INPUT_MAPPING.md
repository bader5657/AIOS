# Exact RegistryPersistenceInput Mapping

## Common fields

| Field | Exact source/value |
|---|---|
| `identity_ref` | `pipeline_result.manifest_path` |
| `represented_media_type` | `recognized_input_type.value` |
| `metadata` | unchanged `pipeline_result.metadata` |
| `relationships` | `[]` |
| `manifest_ref` | `pipeline_result.manifest_path` |
| `registration_status` | `None` |

## Input-specific fields

| Input | `storage_path` | `source_url` |
|---|---|---|
| File-backed approved input | `pipeline_result.stored_path` | `None` |
| Text | `None` | `None` |
| Web Link / YouTube Link | `None` | exact accepted ingestion `text` URL |

Metadata is carried without re-extraction, enrichment, or mutation. Empty
relationships means none and creates no relationship vocabulary.
`manifest_status="created"` must not become registration status. URL values
must not be normalized, retrieved, redirected, or enriched. Original bytes
must not cross the boundary.
