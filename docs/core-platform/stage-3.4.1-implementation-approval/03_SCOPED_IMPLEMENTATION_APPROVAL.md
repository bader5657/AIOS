# Stage 3.4.1 Scoped Implementation Approval

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Implementation authority | **ACTIVE for the exact approved scope only** |
| Exact baseline | `773fc37d01e5205138d91a325fd510c975b80862` |
| Canonical object | `Document Manifest`; `Manifest` is shorthand only |

## Existing Conforming Behavior to Preserve

- There is one `DocumentManifest` runtime concept and one accepted Manifest
  storage boundary: `/opt/aios/data/documents/manifests`.
- Current file-backed creation references the stored path, measures its byte
  size, hashes the bytes with SHA-256, and writes JSON as UTF-8 without binary.
- Universal Ingestion already orders single-file flow as Store Original →
  Extract Metadata → Create Manifest; storage or metadata failure prevents
  Manifest, and no Registry implementation exists.
- Recognition covers all ten approved Stage 3.3 identities; URL metadata uses
  exact received text without network retrieval; metadata rejects `manifest`.

## Required Implementation Delta

Replace legacy `document_id`, `media_type`, `status = stored`, creation-time-as-
received-time, mandatory/synthetic Telegram context, and file-only assumptions
with the active minimum contract: `manifest_id`, canonical
`represented_media_type`, actual UTC RFC 3339 `received_at`,
`manifest_status = created`, and the unchanged bounded successful `metadata`.

Create a conforming Document Manifest after successful metadata for all ten
approved identities. File-backed inputs require `storage_path`, exact
`file_size_bytes`, and lowercase SHA-256 of exact stored-original bytes. Text
without a stored original omits all file-backed properties. Web Link and
YouTube Link require the exact `source_url` and no fetch, redirect resolution,
dereference, download, enrichment, snapshot, or remote metadata lookup.

Only active-authority optional fields may be emitted: deterministic
`created_at` when distinct and deterministic source/request identifiers already
available from request context. Unavailable optional fields are omitted, never
null, guessed, empty, zero placeholders, or synthetic defaults.

## Validation and Serialization

Before an artifact is treated as complete, reject unsupported represented
types (including `manifest`), missing/empty universal or conditional fields,
invalid or timezone-less timestamps, invalid SHA-256, forbidden conditional
field combinations, unknown fields, invalid bounded metadata, and any output
that does not conform to the normative schema. Runtime serialization is JSON
UTF-8, contains no binary, preserves approved primitive types and meaning on
round trip, and writes safely enough that partial failure cannot look complete.

Implementation may use only the standard library and already-present project
capabilities; adding a dependency is not authorized. Internal validation and
exception arrangement may be minimal but must be deterministic and tested. No
second Manifest model, speculative lifecycle state, or speculative field is
authorized.

## Failure and Downstream Contract

Create Manifest begins only after successful Metadata. Any validation,
serialization, or persistence failure propagates as failure, prevents register
readiness, and leaves no valid completed Manifest artifact. Original stored
assets remain untouched. No Registry call, persistence, migration, or execution
is authorized.
