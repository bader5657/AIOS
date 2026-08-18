# Registry Input Mapping Evidence

Verified mapping is exact:

| Field | Accepted value |
|---|---|
| `identity_ref` | completed `pipeline_result.manifest_path` |
| `represented_media_type` | `recognized_input_type.value` |
| `metadata` | unchanged `pipeline_result.metadata` object |
| `relationships` | `[]` |
| `manifest_ref` | completed `pipeline_result.manifest_path` |
| `registration_status` | `None` |
| `storage_path` | accepted stored path where applicable, otherwise `None` |
| `source_url` | exact URL for Web/YouTube Link only, otherwise `None` |

Equal identity/reference values create no canonical equivalence, uniqueness,
deduplication, or Registry ID semantics.
