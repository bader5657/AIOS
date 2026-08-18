# Persistence-Concept Binary-Exclusion Matrix

| Approved concept | Classification | Binary-exclusion result |
|---|---|---|
| `record_id` | Database-local row identity | BIGINT identity; not file content — PASS |
| `identity_ref` | Approved upstream identity/reference | Textual identity only — PASS |
| `represented_media_type` | Approved media/input identity | Textual classification only — PASS |
| `metadata` | Approved Stage 3.3.1 metadata snapshot | Structured JSON object; original bytes/base64/file body prohibited — PASS |
| `relationships` | Approved bounded relationships | Structured JSON array; no file body — PASS |
| `manifest_ref` | Completed Manifest reference | Text reference only; no embedded Manifest — PASS |
| `registration_status` | Optional approved disposition | Nullable text; no file content — PASS |
| `storage_path` | Original-file location reference | Nullable text reference only — PASS |
| `source_url` | Exact applicable source reference | Nullable text reference; no retrieval/content snapshot — PASS |

All nine concepts pass. No approved concept is a binary field, binary type,
original body, or ownership-transfer mechanism.
