# Stage 3.3 Scoped Implementation Approval

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Implementation authority | **ACTIVE for the exact approved scope only** |
| Exact baseline | `3167ca3f2a0eefbd109f984f696b7cd58665a62a` |
| Approved targets | Only the closed-world targets in `01_SCOPED_CHANGE_REQUEST.md` |

## Implementation Contract

The later implementation shall make Metadata Engine produce a bounded metadata
mapping using the active authority's field labels as keys. `media_type` is
required for every approved class and must be supplied from the already
recognized input identity; extraction must not reclassify it.

- Text requires `media_type`; `character_count` may be emitted from exact
  received text.
- Image, Voice, Audio, Video, PDF, DOC/DOCX, and Spreadsheet require
  `media_type` and `file_size_bytes` from the exact preserved original.
- `original_filename`, `mime_type`, `format`, and authorized class-specific
  optional fields may be emitted only when locally and deterministically
  source-derived; otherwise they are omitted.
- Web Link and YouTube Link require `media_type` and the exact received
  `source_url`; no network operation is permitted.
- Fields outside the active minimum contract must not be emitted.

Universal Ingestion may be changed only to pass the already recognized class
and the appropriate preserved source facts to Metadata Engine, including Text
and URL-only inputs, and to treat successful extraction as the gate before the
existing later Manifest call. The active single-original sequence is retained.
The Stage 3.2.2 mixed/multiple-original stop remains unchanged.

## Validation and Failure

- Reject a class outside the ten approved identities, including Manifest.
- Reject missing, invalid, or unavailable required facts.
- Omit rather than synthesize an unavailable or invalid optional value.
- A file-backed input must reference the exact existing preserved original.
- Metadata failure must prevent `Create Manifest`, Register readiness, and all
  later progression; the preserved original is retained and is not deleted or
  rewritten.

The concrete exception arrangement may remain internal, but it must be
deterministic and covered by tests. No new public DTO, schema, persistence
model, dependency, or abstraction is authorized.

## Output and Downstream Boundary

The only approved output is the bounded metadata mapping already carried by
the existing ingestion result. This approval creates no persistence behavior.
Manifest may consume successful metadata later, but is not metadata, is not a
media type, and must not be required, created, inspected, or validated by
Metadata Engine. Register remains a later boundary.

## Acceptance Criteria and Rollback Condition

Acceptance requires an exact allowed-path diff, conformance for all ten input
classes and every required/optional-field rule, preserved lifecycle ordering
and compatibility boundaries, zero network/Manifest/Registry dependency during
extraction, and PASS results for every mandatory verification gate. Review must
find no authority expansion and no unintended runtime or data effect.

Existing accepted classification, storage, single-original flow, original
filename separation, mixed/multiple storage barrier, acknowledgement boundary,
and later handoffs must remain compatible. If any acceptance gate fails, stop,
do not merge or deploy, and revert the scoped implementation commit/PR. No data
migration or stored-original rollback is authorized or required.
