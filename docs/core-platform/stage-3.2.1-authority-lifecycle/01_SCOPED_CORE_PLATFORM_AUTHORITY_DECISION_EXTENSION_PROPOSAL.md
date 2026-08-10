# Stage 3.2.1 Scoped Core Platform Authority Decision Extension — Proposal

## Document Control

| Control | Value |
|---|---|
| Lifecycle transition | **PROPOSAL** |
| Explicit status | **PROPOSED — PASS; NOT APPROVED, PUBLISHED, OR ACTIVE** |
| Current accepted baseline | `362c0ac3b9f572c24a55c0ac57104328868b36ce` |
| Authority trace | Blueprint → Authority Hierarchy → Frozen Roadmap → Canonical Model → Layer Architecture → Core Platform Authority Decision → Execution Plan → Active Stage 3.1.3/3.1.4 → Active Stage 3.2.1 D01–D25 → this scoped extension |
| Scope | Stage 3 → Main Step 3.2 → Sub Step 3.2.1; governance authority only |
| Runtime/implementation effect | **NONE** |

## Rationale and Blocker Register

The accepted baseline already makes Stage 3.2.1 D01–D25 Published and Active.
The latest Stage 3.2.1 scoped-extension review found the added normative detail
complete but non-authoritative because explicit Project Owner Approval,
Publication, and Activation were absent. Those lifecycle gaps are valid
blockers. The proposal also makes the reviewed details self-contained at the
current baseline so that stale-baseline authority is not inferred.

| Valid blocker | Proposal disposition | Evidence | Result |
|---|---|---|---|
| Exact storage filename mechanics absent from D14 | UUID-v4 and extension policy below | D14 expressly deferred the mechanism | **PASS — CONTRACT PROPOSED** |
| Link-original physical representation must not be inferred | Exact URL is the original; physical serialization remains deferred | Active D10, D11, D15 | **PASS — BOUNDED** |
| Partial persistence semantics need an explicit bounded result | Failed request; retained completed originals; no downstream advance or inferred rollback | Active D20–D23 | **PASS — BOUNDED** |
| Approval missing | Separate post-review record required | prior scoped review record | **OPEN UNTIL APPROVAL** |
| Publication missing | Separate accepted-history transition required | GD-002 lifecycle | **OPEN UNTIL PUBLICATION** |
| Activation missing | Separate post-publication transition required | GD-002 lifecycle | **OPEN UNTIL ACTIVATION** |

## Scoped Normative Decision

### Storage-Class to Published-Path Mapping and Disposition

| Storage class / input | Published path | Normative disposition |
|---|---|---|
| Image | `/opt/aios/data/documents/images` | Storage persists exact original file bytes; identity remains Image |
| Voice | `/opt/aios/data/documents/voice` | Storage persists exact original file bytes; identity remains Voice |
| Audio | `/opt/aios/data/documents/voice` | Storage persists exact original file bytes; shared root does not reclassify Audio |
| Video | `/opt/aios/data/documents/images` | Storage persists exact original file bytes; shared root does not reclassify Video |
| PDF | `/opt/aios/data/documents/pdf` | Storage persists exact original file bytes |
| DOC / DOCX | `/opt/aios/data/documents/docs` | Storage persists exact original file bytes; DOC and DOCX identities remain unchanged |
| Spreadsheet | `/opt/aios/data/documents/docs` | Storage persists exact original XLS, XLSX, CSV, or ODS bytes; format identity remains unchanged |
| Web Link | `/opt/aios/data/documents/links` | Storage durably preserves the exact received URL value only; no fetch, file, cache, snapshot, normalization, or metadata substitute |
| YouTube Link | `/opt/aios/data/documents/links` | Same URL-only rule as Web Link; canonical identity remains distinct |
| Manifest | `/opt/aios/data/documents/manifests` | Reserved published path boundary only; Stage 3.2.1 creates, reads, writes, or persists no Manifest |

Each file original is stored exactly once beneath its mapped root. Root sharing
does not share artifacts, merge canonical identities, or authorize copies,
moves, or inferred subdirectories. Universal Ingestion owns the bounded
request/handoff; Storage owns original persistence. Manifest remains owned by
the later Document Manifest boundary.

### Filename and Original-Filename Policy

For file inputs, the stored filename is lowercase canonical UUID version 4
text followed, when valid, by `.` and the lowercase final original extension:
`<uuid-v4>[.<extension>]`. The extension candidate has its leading dot removed
and is accepted only if it contains 1–16 ASCII alphanumeric characters.
Otherwise it is omitted. No original basename character enters the stored
filename. The UUID is generated once; a collision fails immediately with zero
rename or collision retries. Timestamp, hash, suffix, deduplication, overwrite,
replacement, and automatic rename are prohibited.

The exact received original filename value is preserved separately as
descriptive source information, including absence as absence. It is never a
path and is not normalized, transliterated, trimmed, or rewritten. This policy
creates no Metadata field or schema. Links and Manifest have no filename under
this extension.

### Link-Original Representation

For Web Link and YouTube Link, the exact received URL value is the original.
Successful Storage means that exact value is durably preserved within the
`links` ownership boundary. It is not metadata and is never replaced by or
combined with downloaded content. The physical serialization mechanism remains
deferred and must not be inferred by implementation, review, or activation.

### Migration / Non-Migration Policy

The decision is **NON-MIGRATION**. There is no migration owner. Existing or
legacy data must not be scanned, reconciled, read for migration, renamed,
moved, copied, deleted, converted, deduplicated, backfilled, or relocated.
Legacy and future artifacts may coexist without either overwriting the other.
This contract applies only to future persistence after separate implementation
authority; it does not retroactively classify existing data.

### Bounded Success and Failure Disposition

Success exists only when every original in one bounded Store Original request
has completed durable persistence at its assigned boundary. File success means
exact original bytes exist at the exclusive new target; Link success means the
exact URL value is durably preserved. Success returns semantic Storage
readiness only and claims nothing about Metadata or later pipeline stages.

Collision, write, directory, validation-at-storage-boundary, or persistence
failure produces bounded request failure and stops before Metadata. Partial
persistence is request failure: completed originals remain retained and must
be identified only in the bounded semantic disposition; they grant no
downstream progress. No retry, rollback, deletion, compensation, transaction,
cleanup, error payload, response schema, exception type, or runtime algorithm
is authorized.

## Preservation and Extension Tests

| Required architectural determination | Evidence | Result |
|---|---|---|
| Canonical Model extension | No new canonical object, identity, field, schema, or equivalence is introduced | **PASS — NOT REQUIRED** |
| Layer Architecture extension | No dependency direction changes; existing Ingestion → Storage permission is preserved | **PASS — NOT REQUIRED** |
| Blueprint modification | Blueprint inputs, roots, lifecycle, and Store Original invariant remain unchanged | **PASS — NONE** |
| Execution Plan modification | Stage 3.2.1 remains the storage-path and non-migration decision boundary | **PASS — NONE** |
| Authority Hierarchy / Frozen Roadmap | Existing authority class and phase boundary are preserved | **PASS — NONE** |

## Stop Conditions

Stop immediately on a missing or inferred mapping; inferred URL serialization;
Manifest creation or persistence; original-filename use as a path; overwrite,
rename, retry, rollback, compensation, migration, or existing-data contact;
Metadata/Registry/Event Engine/AIOS Core/Brain/Router/Specialist work; new
canonical object, layer, dependency, schema, configuration, deployment, source,
test, or runtime modification; lifecycle reorder; or any failed verification.

## Stage Evidence

| Evidence class | Evidence | Result |
|---|---|---|
| Review evidence | Prior scoped extension review at accepted commit `0091561`; fresh review still required for this baseline-bound proposal | **PASS — AVAILABLE; NOT A FRESH TRANSITION** |
| Approval evidence | None at Proposal | **PASS — CORRECTLY ABSENT** |
| Verification evidence | Scope, authority trace, required mapping, compatibility, dependency, runtime, and extension tests above | **PASS** |

**PROPOSAL STATUS: PASS — PROPOSED; NO AUTHORITY EFFECT**
