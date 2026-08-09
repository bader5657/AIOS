# Stage 3.2.2 Core Platform Authority Decision Extension

| Control | Value |
|---|---|
| Lifecycle | **DRAFT** |
| Extension target | Existing Core Platform Authority Decision — Storage Path Contract only |
| Baseline | `79448eab8b343ee09b141bc73faeba767e6b92e4` |
| Subject | Preserve every original file before any processing begins |
| Implementation/runtime effect | **NONE** |

## 1. Normative Invariant

For one bounded received request, every recognized canonical **file original**
must complete Storage persistence before Metadata extraction, Manifest creation,
Register, Process, Route, Respond, or any other processing begins for any member
of that request. A bounded Store Original failure prevents all downstream
progress for the request.

Web Link and YouTube Link remain exact URL-only, non-file originals under Active
Stage 3.2.1 authority. Manifest remains a later boundary and is not an original.
Neither is silently reclassified as a file for Stage 3.2.2.

## 2. Complete Canonical Disposition

Common file policy **F** means: generated lowercase UUID v4 plus the accepted
lowercase final extension; extension is 1–16 ASCII alphanumeric characters or
omitted; exact received original filename is preserved separately and never
used as a path; exclusive-create; first collision fails; no overwrite,
automatic rename, timestamp/hash naming, or retry. Common compatibility **C**
means canonical identity, lifecycle order, layer direction, and Stage 3.2.1
storage contract remain unchanged. Common migration **N** means non-migration
and existing runtime data NO TOUCH.

| Canonical input | Storage class / published destination | Filename / original filename | Metadata responsibility | Ownership | Migration / compatibility / failure |
|---|---|---|---|---|---|
| Image | `images` → `/opt/aios/data/documents/images` | F; missing source name remains absent | Metadata Engine only, after all file storage succeeds | Storage persists; Universal Ingestion owns request/handoff | N; C; bounded request failure stops before Metadata |
| Voice | `voice` → `/opt/aios/data/documents/voice` | F; absence remains absence | Metadata Engine only after aggregate storage success | Storage persists; Universal Ingestion owns request/handoff | N; C; bounded request failure stops before Metadata |
| Audio | `voice` → `/opt/aios/data/documents/voice`; identity remains Audio | F; exact received name or absence preserved separately | Metadata Engine only after aggregate storage success | Storage persists; root sharing does not reclassify Audio | N; C; bounded request failure stops before Metadata |
| Video | `images` → `/opt/aios/data/documents/images`; identity remains Video | F; exact received name or absence preserved separately | Metadata Engine only after aggregate storage success | Storage persists; root sharing does not reclassify Video | N; C; bounded request failure stops before Metadata |
| PDF | `pdf` → `/opt/aios/data/documents/pdf` | F; exact received name preserved separately | Metadata Engine only after aggregate storage success | Storage persists; Universal Ingestion owns request/handoff | N; C; bounded request failure stops before Metadata |
| DOC | `docs` → `/opt/aios/data/documents/docs` | F; exact received name preserved separately | Metadata Engine only after aggregate storage success | Storage persists; Universal Ingestion owns request/handoff | N; C; bounded request failure stops before Metadata |
| DOCX | `docs` → `/opt/aios/data/documents/docs` | F; exact received name preserved separately | Metadata Engine only after aggregate storage success | Storage persists; identity remains DOC/DOCX contract identity | N; C; bounded request failure stops before Metadata |
| Spreadsheet | `docs` → `/opt/aios/data/documents/docs` | F for XLS/XLSX/CSV/ODS; exact name preserved separately | Metadata Engine only after aggregate storage success | Storage persists; format identity is preserved | N; C; bounded request failure stops before Metadata |
| Web Link | `links` ownership root → `/opt/aios/data/documents/links` | No filename; exact received URL preserved without normalization | No Stage 3.2.2 metadata authority | Storage owns URL-original preservation; no fetch/file fallback | N; C; failure remains bounded; excluded from file-ordering matrix |
| YouTube Link | `links` ownership root → `/opt/aios/data/documents/links`; URL-only | No filename; exact received URL without normalization | No Stage 3.2.2 metadata authority | Storage owns URL-original preservation; identity remains distinct | N; C; bounded failure; excluded from file-ordering matrix |
| Manifest | Reserved boundary → `/opt/aios/data/documents/manifests` | No Stage 3.2.2 filename or original-filename policy | Created only after Metadata under later Manifest authority | Document Manifest boundary; Storage gains no owner grant | N; C; no Stage 3.2.2 persistence operation |

No row authorizes Metadata fields, schema, URL serialization, Manifest
representation, PostgreSQL schema, or a new canonical object.

## 3. Mixed and Multiple Original Disposition

1. Every distinct recognized file-original simultaneously exposed by one
   received Telegram request is a member of one bounded Store Original request.
2. No media precedence, winner selection, fallback, silent discard, identity
   collapse, or single-attachment assumption is permitted.
3. Each member is persisted exactly once to its explicit root. Internal
   iteration order is non-canonical and may be fixed by implementation, but it
   cannot change identity or disposition and must be deterministic and tested.
4. Metadata and all later actions begin only after **all** members report
   bounded persistence success.
5. If any member fails, the request disposition is failure. Successfully
   persisted members remain retained; rollback, deletion, compensation, retry,
   rename, or transaction mechanics are not authorized. Partial persistence
   never authorizes downstream progress.
6. Caption/text may coexist as received transport content but is not a file
   original and does not bypass the all-file-original barrier.

## 4. Preservation, Manifest, and PostgreSQL Boundaries

- Preservation means exact original file bytes at the newly exclusive-created
  target, or the exact URL value under the existing non-file Link contract.
- Manifest remains after successful Storage and Metadata. Stage 3.2.2 creates
  no Manifest schema, file, filename, or persistence authority.
- PostgreSQL Registry responsibility begins only at the later `Register`
  boundary after a completed Manifest disposition. Storage and Universal
  Ingestion must not write PostgreSQL or create a Registry reference, row,
  schema, transaction, or runtime. Any future stored-path/URL reference shape
  remains outside Stage 3.2.2.

## 5. Compatibility Contract

The official sequence remains:

```text
Receive -> Store Original -> Extract Metadata -> Create Manifest
        -> Register -> Process -> Route -> Respond
```

Stage 3.1.3 canonical recognition and mixed-input identity preservation remain
unchanged. Stage 3.1.4 ownership and bounded handoffs remain unchanged. Stage
3.2.1 paths, filename, collision, overwrite, URL-only, partial-failure, and
non-migration decisions remain unchanged. No Blueprint, Canonical Model,
Authority Hierarchy, Frozen Roadmap, Layer Architecture, dependency, runtime,
schema, or downstream owner is changed.

## 6. Failure and Stop Contract

Download, validation-at-storage-boundary, directory creation, read, write,
collision, or persistence failure produces only bounded Store Original failure.
No Metadata or later action may run. Work stops on an unrecognized/inferred
class, missing explicit root, attempted overwrite/rename/retry, runtime-data
contact, link serialization, Manifest persistence, PostgreSQL access, pipeline
reorder, downstream runtime, dependency/schema growth, non-approved file, or
failed verification.
