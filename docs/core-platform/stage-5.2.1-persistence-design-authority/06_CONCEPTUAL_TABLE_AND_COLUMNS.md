# Conceptual Table and Column Design

## Table: `registry_records`

| Column | Conceptual PostgreSQL type | Presence | Responsibility/limit |
|---|---|---|---|
| `record_id` | `BIGINT GENERATED ALWAYS AS IDENTITY` | Required, database generated | Database-local primary key; no domain or business meaning |
| `identity_ref` | Text | Required | Exact approved upstream identifier/reference; Registry does not generate or reinterpret it |
| `represented_media_type` | Text | Required | Approved upstream media/input identity; no reclassification |
| `metadata` | JSONB | Required | Snapshot/copy of approved Stage 3.3.1 metadata; JSON object only |
| `relationships` | JSONB | Required | Approved bounded relationship values; JSON array only; empty array represents none |
| `registration_status` | Text | Optional/nullable | Already-approved upstream status/disposition only; no enum |
| `storage_path` | Text | Optional/nullable | Storage reference only; never binary |
| `source_url` | Text | Optional/nullable | Exact approved URL where applicable; no retrieval or normalization |
| `manifest_ref` | Text | Required | Reference to completed Document Manifest; no embedded Manifest |

This is an approved persistence design, not executable DDL. Missing optional
values remain absent/null and must never be fabricated. Exact length limits,
collations, physical storage settings, ownership grants, and deployment names
are not authorized here.
