# Core Platform Stage 3.3.1 Metadata Authority Package

## Document Control

| Control | Value |
|---|---|
| Stage position | Stage 3 → Main Step 3.3 → Sub Step 3.3.1 |
| Document class | Metadata Authority Package |
| Status | **APPROVED — PUBLISHED — ACTIVE** |
| Accepted baseline | `8ac29333d54bb499528154704bd4dcbd130a6da4` |
| Approval authority | Project Owner |
| Authority effect | **ACTIVE METADATA CONTRACT** |
| Implementation authority | **NONE** |

This package establishes the minimum semantic metadata contract. It is not a
runtime payload, programming type, JSON Schema, database schema, extraction
algorithm, or implementation approval. Current code, schemas, tests, and
runtime behavior do not establish or enlarge this contract.

## 1. Scope

The approved Universal Ingestion media/input classes are exactly:

- Text;
- Image;
- Voice;
- Audio;
- Video;
- PDF;
- DOC/DOCX;
- Spreadsheet (`XLS`, `XLSX`, `CSV`, `ODS`);
- Web Link; and
- YouTube Link.

Text is included. Manifest is not an approved media/input class. This package
defines no `media_type = manifest` value and no metadata-extraction contract
for a manifest artifact.

The contract is closed and minimum: fields not listed are not authorized by
implication. Optional means the field may be omitted without failing metadata
extraction.

## 2. Authority and Lifecycle Constraints

The package preserves the active authority boundaries for Universal Ingestion,
Metadata Engine, Storage, Document Manifest, and Registry without defining
their implementation. The controlling lifecycle is:

```text
Store Original → Extract Metadata → Create Manifest → Register
```

Consequently:

1. extraction begins only after successful original preservation;
2. metadata describes the accepted input or already-preserved original;
3. extraction success cannot depend on a manifest, because manifest creation
   is later;
4. a manifest identifier or relationship may be added only as a downstream
   artifact/relationship after successful extraction and successful
   `Create Manifest`; and
5. Register remains later work and is not performed or designed here.

Manifest contents, construction, serialization, path, checksum, size, MIME,
identity, parent relationship, and persistence are outside Stage 3.3.1.

## 3. Requiredness and Value Rules

A field is Required only when it can be obtained deterministically within the
Stage 3.3.1 boundary from:

- the accepted input-class identity;
- the exact already-preserved original bytes; or
- the exact already-received URL for URL-only input.

Required fields must not depend on network retrieval, rendering, content
interpretation, enrichment, external services, guessing, synthetic defaults,
or later lifecycle artifacts. Optional fields must also be source-derived; if
not deterministically available they are omitted.

The field labels below express business meaning only. They do not prescribe
classes, keys, casing, serialization, storage, parsing libraries, or database
columns.

## 4. Common Minimum Contract

### 4.1 All approved classes

| Field | Presence | Business meaning |
|---|---|---|
| `media_type` | Required | The already-accepted Universal Ingestion class identity; one of the ten classes in Scope |

`media_type` records the accepted class; Stage 3.3.1 does not guess or
reclassify it.

### 4.2 File-backed classes

Applies to Image, Voice, Audio, Video, PDF, DOC/DOCX, and Spreadsheet.

| Field | Presence | Business meaning |
|---|---|---|
| `file_size_bytes` | Required | Size of the exact already-preserved original in bytes |
| `original_filename` | Optional | Exact received filename, only when the source supplied one |
| `mime_type` | Optional | Source-declared or locally identifiable MIME value, only when deterministically available |
| `format` | Optional | Locally identifiable source/container format, only when deterministically available without rendering or interpretation |

No timestamp, extraction status, checksum, storage path, or manifest reference
is part of the minimum extraction metadata contract. Existing lifecycle
dispositions and storage handoffs remain separate boundary facts.

### 4.3 URL-only classes

Applies to Web Link and YouTube Link.

| Field | Presence | Business meaning |
|---|---|---|
| `source_url` | Required | Exact already-received URL that satisfied the active local recognition boundary |

URL metadata must not require dereference, redirects, remote MIME, remote title,
description, thumbnail, duration, channel data, or any other network-derived
value.

## 5. Per-Class Metadata Contract

Each table includes the common fields applicable to that class so requiredness
can be audited without inference.

### Text

| Required | Optional |
|---|---|
| `media_type` | `character_count` |

`character_count`, when supplied, is counted from the exact received text. No
language detection, summary, classification, tokenization, or semantic/content
interpretation is metadata in minimum v1.

### Image

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `width_pixels`, `height_pixels`, `orientation`, `color_mode` |

Optional properties must be explicit source/container properties obtainable
locally without rendering or visual interpretation.

### Voice

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `duration_seconds`, `codec`, `sample_rate_hz`, `channel_count`, `bit_rate_bps` |

### Audio

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `duration_seconds`, `codec`, `sample_rate_hz`, `channel_count`, `bit_rate_bps`, `title`, `artist` |

`title` and `artist` are permitted only as exact embedded properties. Their
absence is valid and content analysis is prohibited.

### Video

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `duration_seconds`, `width_pixels`, `height_pixels`, `video_codec`, `audio_codec`, `frame_rate_fps`, `bit_rate_bps` |

Optional values must come from locally available source/container structure;
no frame rendering or audiovisual interpretation is permitted.

### PDF

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `page_count`, `title`, `author`, `created_at`, `modified_at` |

Document properties are exact embedded values only. Page count is omitted when
it cannot be obtained locally without rendering. Timestamps are omitted when
their timezone or meaning would require guessing.

### DOC/DOCX

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `page_count`, `word_count`, `title`, `author`, `created_at`, `modified_at` |

Page and word counts are permitted only when explicitly present as locally
available document properties; no rendering or content traversal is required.

### Spreadsheet

| Required | Optional |
|---|---|
| `media_type`, `file_size_bytes` | `original_filename`, `mime_type`, `format`, `sheet_count`, `sheet_names`, `author`, `created_at`, `modified_at` |

Structural and document properties are optional and locally source-derived.
Cell reading, formula evaluation, inferred tables, summaries, and content
classification are outside minimum v1.

### Web Link

| Required | Optional |
|---|---|
| `media_type`, `source_url` | None |

### YouTube Link

| Required | Optional |
|---|---|
| `media_type`, `source_url` | None |

The YouTube class remains subject to its active local URL-recognition boundary.
No video ID, playlist ID, channel, title, thumbnail, or remote media property is
required or authorized here.

## 6. Validation and Failure Boundary

1. A missing or invalid Required field makes metadata extraction unsuccessful
   for that input.
2. A present Optional field must be exact and source-derived; otherwise it is
   omitted rather than guessed, coerced, enriched, or synthesized.
3. File-backed values describe the exact preserved original, not a converted,
   transcoded, rendered, repaired, or temporary derivative.
4. Metadata failure stops the lifecycle before `Create Manifest` and
   `Register`.
5. These semantic outcomes prescribe no payload, exception, parser, library,
   retry, transaction, or aggregate implementation.

## 7. Ownership, Persistence, and Manifest Relationship

| Concern | Boundary |
|---|---|
| Extraction request | Universal Ingestion requests extraction only after successful original preservation |
| Extraction | Metadata Engine produces the bounded metadata disposition |
| Original preservation | Storage remains responsible for the original; Stage 3.3.1 does not alter storage |
| Manifest | Document Manifest may consume successful metadata and create a later artifact/relationship |
| Register | Registry persistence occurs only at the later authorized lifecycle step |

A downstream manifest relationship is not a media type and is not extraction
metadata. If a later authority defines such a relationship, it may be attached
only after successful `Create Manifest`; it must not be required, populated, or
validated by `Extract Metadata`.

## 8. Explicit Exclusions

This package does not authorize:

- changes to Stage 3.2.1, runtime, tests, the Blueprint, or Frozen Roadmap;
- source code, configuration, schemas, database work, migration, or deployment;
- a JSON or database schema, DTO, API, canonical object, or persistence design;
- network retrieval, rendering, content interpretation, enrichment, guessing,
  conversion, transcoding, or original mutation;
- manifest construction or treating Manifest as an input/media class;
- implementation target selection or Stage 3.3 implementation; or
- modification of production data or services.

## 9. Approval Checklist

- [x] Confirm baseline `8ac29333d54bb499528154704bd4dcbd130a6da4`.
- [x] Approve exactly the ten media/input classes, including Text.
- [x] Confirm Manifest is not a media/input class and `media_type = manifest`
      is prohibited.
- [x] Approve every Required and Optional field in Section 5.
- [x] Approve the deterministic-requiredness and omission rules.
- [x] Confirm the exact lifecycle order and downstream-only Manifest boundary.
- [x] Confirm the contract is semantic and implementation-independent.
- [x] Confirm approval does not authorize implementation, tests, schema work,
      runtime work, or any later lifecycle stage.

## Final Status

**APPROVED — PUBLISHED — ACTIVE**

**METADATA AUTHORITY ACTIVE — NO IMPLEMENTATION AUTHORIZED**
