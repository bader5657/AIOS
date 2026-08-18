# Approved Schema Realization

The migration realizes only `registry_records`:

| Column | Exact SQL-level design |
|---|---|
| `record_id` | `BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY` |
| `identity_ref` | `TEXT NOT NULL` |
| `represented_media_type` | `TEXT NOT NULL` |
| `metadata` | `JSONB NOT NULL` |
| `relationships` | `JSONB NOT NULL DEFAULT '[]'::jsonb` |
| `manifest_ref` | `TEXT NOT NULL` |
| `registration_status` | `TEXT NULL` |
| `storage_path` | `TEXT NULL` |
| `source_url` | `TEXT NULL` |

Required CHECK constraints verify `jsonb_typeof(metadata) = 'object'` and
`jsonb_typeof(relationships) = 'array'` only.

No binary type/body, status/media vocabulary constraint, secondary index,
uniqueness beyond the primary key, foreign key, extension, timestamp, checksum,
or business column is authorized.
