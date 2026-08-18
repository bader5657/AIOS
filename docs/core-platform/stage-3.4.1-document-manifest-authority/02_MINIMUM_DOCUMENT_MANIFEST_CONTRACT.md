# Stage 3.4.1 Minimum Document Manifest Contract

## 1. Contract Character

This is the authoritative minimum closed v1 semantic and serialization
contract. The normative machine-readable realization, after reconciliation, is
`config/ingestion-manifest.schema.json`. Runtime output must validate against
that schema. The current file is drift/example evidence and is not promoted by
this record without correction.

The normative schema must be valid JSON Schema, declare `$schema`, define a root
object/type, `properties`, `required`, and `additionalProperties: false`, and
match runtime serialization.

## 2. Universal Required Fields

| Field | Approved type and meaning |
|---|---|
| `manifest_id` | Non-empty string; unique opaque identifier generated at the Manifest creation boundary; deterministic-enough for unique artifact identity; no business meaning may be inferred |
| `represented_media_type` | Non-empty string identifying exactly one approved Stage 3.3 input class; never `manifest` |
| `received_at` | Non-empty UTC RFC 3339 string; preserves the received timestamp without guessing timezone |
| `manifest_status` | String constant `created` for every successfully serialized Document Manifest |
| `metadata` | Non-empty bounded object containing the successful, already-validated Stage 3.3.1 metadata result without re-extraction, mutation, or semantic expansion |

`metadata` is the approved minimum representation because the current
architecture already returns the bounded Stage 3.3 result to Universal
Ingestion. Stage 3.3.1 remains the authority for every metadata field; the
Document Manifest is a consumer and carrier, not a new metadata authority.

## 3. Conditional Required Fields

For an input with an accepted stored original binary, all fields below are
required:

| Field | Approved type and meaning |
|---|---|
| `storage_path` | Non-empty reference string to the accepted stored original; content remains external |
| `file_size_bytes` | Integer greater than or equal to zero representing the exact stored original byte length |
| `checksum_sha256` | Non-empty lowercase 64-hex string computed over the exact stored original bytes |

For URL-only Web Link and YouTube Link inputs, `source_url` is required and is
the exact received URL. The creation boundary must not fetch, download,
dereference, enrich, redirect-resolve, or snapshot the remote content.

Text does not require file-backed fields. If Text arrives as an accepted stored
file-backed artifact, all three file-backed fields become required. A URL-only
or non-file-backed Text input has no binary checksum requirement.

## 4. Approved Input Applicability

| Input | Required relationship beyond universal fields |
|---|---|
| Text | None, unless file-backed; then stored-original fields |
| Image | Stored-original fields |
| Voice | Stored-original fields |
| Audio | Stored-original fields |
| Video | Stored-original fields |
| PDF | Stored-original fields |
| DOC/DOCX | Stored-original fields |
| Spreadsheet | Stored-original fields |
| Web Link | Exact `source_url` |
| YouTube Link | Exact `source_url` |

The represented media type uses the canonical recognized Stage 3.3 identity,
including PDF, DOC/DOCX, Spreadsheet, Web Link, and YouTube Link; legacy
pipeline compatibility types must not replace it.

## 5. Optional Fields

Only the following optional fields are authorized in minimum v1:

- `created_at`: UTC RFC 3339 creation timestamp, only when distinct from
  `received_at` and deterministically captured at the creation boundary;
- existing deterministic source/request identifiers already available in
  request context, including Telegram identifiers; they remain contextual
  relationships and never become universal business identity.

The normative schema must name any selected source/request fields explicitly;
no free-form extension bag is authorized. Unavailable optional fields are
omitted, never null, empty-string, zero-placeholder, guessed, or synthetically
defaulted.

## 6. Value, Serialization, and Storage Rules

- Required fields cannot be null, empty, or omitted. Numeric zero is valid only
  where it is the exact measured value, such as an empty stored original.
- Canonical serialization is JSON encoded as UTF-8. No binary is embedded.
- Round-trip serialization preserves meaning and approved primitive types.
- The artifact uses the accepted manifest storage boundary
  `/opt/aios/data/documents/manifests`; no new root is authorized.
- `storage_path` refers to the original. Creating a Document Manifest neither
  stores nor mutates the original binary.
- Document Manifest checksum semantics do not replace or redefine original-file
  checksum semantics.

## 7. Failure Contract

Create Manifest starts only after successful Metadata. Schema construction,
validation, serialization, or persistence failure stops before Register. A
partial or failed artifact is not a valid Document Manifest and must be removed
or remain clearly non-valid under the simplest safe implementation. Register
must never execute after Manifest failure. Stage 3.4.1 does not implement
Registry.
