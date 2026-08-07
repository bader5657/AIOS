# Core Platform Stage 3.2.1 Scoped Authority Extension

## Document Control

| Field | Value |
|---|---|
| Authority class | Proposed scoped extension to `CORE_PLATFORM_AUTHORITY_DECISION.md` |
| Status | **REVIEWED — PASS; AWAITING PROJECT OWNER APPROVAL** |
| Accepted baseline | `f4f49fd6df7535f409f9659edafcf5ed2d9f58a3` |
| Official position | Stage 3 → Main Step 3.2 → Sub Step 3.2.1 |
| Governing authority | Published and Active authority only |
| Implementation authority | **NONE** |
| Runtime effect | **NONE** |
| Publication/activation effect | **NONE UNTIL SEPARATELY REVIEWED, APPROVED, PUBLISHED, AND ACTIVATED** |

This document extends only the existing Core Platform Authority Decision. It
does not amend the Blueprint, Canonical Model, Layer Architecture, Frozen
Roadmap, Execution Plan, Registry, Event Engine, AIOS Core, or the Stage 3.1.3
and Stage 3.1.4 lifecycle contracts. Its normative statements are explicit
extension decisions, not inferences from storage-root names.

## 1. Scoped Authority Decision

The Project Owner is asked to approve the following complete Stage 3.2.1
contract as one indivisible governance decision. Approval supplies authority
content only. It does not authorize implementation or make this proposal
Published or Active.

### 1.1 Storage Mapping and Disposition

`Published root` is the authority-approved persistence classification. For
file inputs it is a filesystem directory. For link inputs it is the ownership
root for the durable URL value; the active URL-only/non-file restriction is
preserved. For Manifest it is only the already-authorized future path boundary;
Stage 3.2.1 neither creates nor persists a Manifest.

| Input type | Persistence owner | Published storage root | Sharing rule | Path ownership | Stored representation |
|---|---|---|---|---|---|
| Image | Storage | `/opt/aios/data/documents/images` | One persisted original may be referenced downstream only after storage success; no cross-root copy or move | Storage owns the target beneath the published root; Universal Ingestion owns only the request | Exact original file bytes under a generated storage filename |
| Voice | Storage | `/opt/aios/data/documents/voice` | Same persisted-original reference rule; no sharing by duplication | Same Storage/request boundary | Exact original file bytes under a generated storage filename |
| Audio | Storage | `/opt/aios/data/documents/voice` | Shares the root with Voice but not canonical identity, filename, or persisted artifact | Same Storage/request boundary | Exact original file bytes under a generated storage filename |
| Video | Storage | `/opt/aios/data/documents/images` | Shares the root with Image but not canonical identity, filename, or persisted artifact | Same Storage/request boundary | Exact original file bytes under a generated storage filename |
| PDF | Storage | `/opt/aios/data/documents/pdf` | Same persisted-original reference rule; no cross-root copy or move | Same Storage/request boundary | Exact original file bytes under a generated storage filename |
| DOC | Storage | `/opt/aios/data/documents/docs` | Shares the root with DOCX and Spreadsheet but not identity, filename, or artifact | Same Storage/request boundary | Exact original file bytes under a generated storage filename |
| DOCX | Storage | `/opt/aios/data/documents/docs` | Shares the root with DOC and Spreadsheet but not identity, filename, or artifact | Same Storage/request boundary | Exact original file bytes under a generated storage filename |
| Spreadsheet | Storage | `/opt/aios/data/documents/docs` | Shares the root with DOC/DOCX but not identity, filename, or artifact | Same Storage/request boundary | Exact original XLS, XLSX, CSV, or ODS file bytes under a generated storage filename |
| Web Link | Storage | `/opt/aios/data/documents/links` | The preserved URL value may be referenced after persistence success; it is not shared as downloaded content | Storage owns durable preservation within the `links` root; Universal Ingestion owns only the request | Exact received original URL value, URL-only and non-file; no metadata-only substitute |
| YouTube Link | Storage | `/opt/aios/data/documents/links` | Same rule as Web Link while canonical identity remains distinct | Same Storage/request boundary | Exact received original URL value, URL-only and non-file; no metadata-only substitute |
| Manifest | Document Manifest boundary for creation; no Stage 3.2.1 persistence owner is granted | `/opt/aios/data/documents/manifests` | No Manifest is shared, created, read, or written under this extension | The published root remains reserved for the later Document Manifest authority; Storage receives no ownership grant here | **NONE in Stage 3.2.1**; path boundary only, with schema and representation deferred to Stage 3.4 authority |

Root sharing never means artifact sharing, canonical reclassification, or
permission to infer a subdirectory. No input may be stored in a root other than
the row explicitly assigned above.

### 1.2 Link Representation Contract

For both Web Link and YouTube Link:

| Question | Normative decision |
|---|---|
| Is the original URL stored? | **YES.** The exact received URL value is the original and is durably preserved. |
| Metadata only? | **NO.** The URL is the original value, not a metadata-only replacement. No metadata is created by this extension. |
| Downloaded file? | **NO.** Fetch, dereference, redirect traversal, download, cache, snapshot, and remote-content persistence are prohibited. |
| Both URL and file? | **NO.** URL only. |
| Ownership | Storage owns durable URL preservation; Universal Ingestion owns only the bounded request and result handoff. |
| Persistence boundary | Completion occurs only when the exact received URL value is durably preserved within the `links` ownership root. The physical serialization mechanism remains outside this governance-only extension and must not be inferred. |

No URL normalization, enrichment, canonical-host change, metadata extraction,
or host-recognition change is authorized.

### 1.3 Filename Contract

This contract applies only to file inputs. Link inputs and Manifest have no
filename under this extension.

| Element | Normative decision |
|---|---|
| Original filename | Preserve the exact received filename value separately from the stored filename. It is descriptive source information only and is never used as a path. This does not authorize a Metadata schema or Metadata lifecycle step. |
| Generated filename | Generate one RFC 4122/9562 UUID version 4 value, lowercase canonical text, followed by the normalized original extension when an extension exists: `<uuid-v4>[.<extension>]`. |
| Sanitization | No character from the original basename enters the storage filename. Remove a leading dot from the extension candidate; accept the extension only when every remaining character is ASCII alphanumeric and its length is 1–16. Otherwise omit it. Path separators, traversal components, control characters, whitespace, shell metacharacters, and non-ASCII characters therefore cannot enter the storage filename. |
| Normalization | Lowercase the UUID and accepted extension. Do not Unicode-normalize, transliterate, trim, rewrite, or otherwise mutate the preserved original filename value. |
| Empty/missing filename | Preserve the received absence as absence; generate `<uuid-v4>` with no extension. |

The generated name supplies storage identity only. It does not create a
canonical object, metadata schema, Registry identity, or deduplication key.

### 1.4 Collision Policy

| Mechanism | Decision |
|---|---|
| Preserve original name as target | **NO** |
| UUID | **YES — UUID v4, generated once before target selection** |
| Timestamp | **NO** |
| Numeric or textual suffix | **NO** |
| Content hash | **NO** |
| Automatic rename | **NO** |
| Retry after collision | **NO — zero retries** |
| Collision result | If the generated target already exists, fail the affected persistence operation immediately. Existing content is untouched. |
| Exhaustion behavior | Because retry count is zero, the first collision is retry exhaustion and produces request failure before Metadata. |

This explicitly specializes the Active `unique filename` invariant without
changing the Active `collision fails; no automatic rename` decision.

### 1.5 Overwrite Policy

| Question | Normative decision |
|---|---|
| Overwrite allowed | **NO** |
| Conditional overwrite | **NO conditions permit overwrite** |
| Atomic replacement of existing target | **PROHIBITED** |
| Replace-on-match/deduplicate | **PROHIBITED** |
| Existing-target handling | Fail before changing the existing target |
| Rollback rule | No committed existing artifact may be rolled back, replaced, or mutated. An unpublished write that fails is not success and must not be acknowledged as persisted. Cleanup/transaction mechanics are not authorized here. |

### 1.6 Migration Decision and Existing Files

The decision is **NON-MIGRATION**.

| Subject | Normative decision |
|---|---|
| Migration owner | None |
| Existing/legacy files | No scan, read for reconciliation, rename, move, copy, delete, backfill, conversion, deduplication, or relocation |
| Future files | The contract applies only to persistence requests occurring after this extension becomes Published and Active and after a separately approved implementation exists |
| Compatibility | Legacy paths and names remain untouched and valid under their prior authority; this extension makes no claim about their conformance to the future filename contract |
| Coexistence | Legacy and future artifacts may coexist under published roots; neither may overwrite the other |
| Rollback | Not applicable because no migration occurs |

### 1.7 Success Contract

Full success exists only when every original included in one bounded Store
Original request has completed durable persistence under its assigned root,
with its required original representation intact, and no collision or write
failure occurred. For a file, completion means exact original bytes are
durably present at the newly selected target. For a link, completion means the
exact received URL value is durably preserved within the `links` ownership
root. Manifest is not a Store Original input in this extension.

Partial storage is never success. If any member fails, request disposition is
failure even if another member reached persistence. This governance decision
does not authorize a transaction, compensation, deletion, or rollback
mechanism; consequently any partial persistence is retained, explicitly
reported as partial persistence within the bounded failure disposition, and
must not advance downstream.

Persistence completion makes only a bounded acknowledgement of Store Original
readiness available to Universal Ingestion. It does not acknowledge Metadata,
Manifest, Register, Process, Route, Respond, or business completion.

### 1.8 Failure Contract

| Failure | Required disposition | Downstream effect |
|---|---|---|
| Storage failure | Request failure; no persistence-complete claim | Stop before Metadata |
| Collision failure | Immediate failure; existing target untouched | Stop before Metadata |
| Write failure | Failure; incomplete/uncommitted write is not an original-preservation success | Stop before Metadata |
| Rollback failure | No rollback is authorized. If an external cleanup attempt fails, the request remains failed and the residual is not treated as successfully persisted authority evidence | Stop before Metadata and require separate remediation authority |
| Retry exhaustion | First collision exhausts the zero-retry policy; all other automatic retries are unauthorized | Stop before Metadata |
| Partial persistence | Request failure; identify that persistence is partial in the bounded semantic disposition; retained successful originals do not authorize downstream progress | Stop before Metadata |

No exception type, payload, API, response object, retry scheduler, rollback
algorithm, transaction, or cleanup implementation is defined.

## 2. Compatibility Contract

| Preserved authority | Verification statement |
|---|---|
| Stage 3.1.3 recognition | Input identities, accepted formats, validators, and recognition boundaries are unchanged. Storage-root sharing never reclassifies an input. |
| Stage 3.1.4 lifecycle | Receive → Store Original → Extract Metadata → Create Manifest → Register → Process → Route → Respond is unchanged. |
| Store Original invariant | Every applicable original must be persisted before any processing or Metadata handoff. |
| Manifest order | Manifest remains after Metadata; this extension neither creates nor persists it. |
| Downstream stop | Any Store Original request failure stops before Metadata and all later actions. |
| Registry boundary | No Registry schema, entry, transaction, runtime, or persistence authority. |
| Event Engine boundary | No Event, delivery, process runtime, or Event Engine authority. |
| AIOS Core boundary | No routing, response generation, Brain, Specialist, or AIOS Core authority. |

## 3. Runtime and Dependency Boundary Verification

| Check | Result | Basis |
|---|---|---|
| New layer | PASS — none | Existing seven-layer set unchanged |
| New dependency | PASS — none | Existing Ingestion → Storage permission only |
| Storage → Brain/Specialist | PASS — prohibited and absent | Active Layer Architecture |
| Canonical object | PASS — none | Filenames and bounded dispositions are non-canonical |
| Runtime behavior | PASS — none authorized | Governance-only scope |
| Source/config/test/migration/deployment | PASS — none authorized | Explicit stop boundary |

## 4. Stop Conditions

This extension stops exactly when Store Original persistence has either
completed or failed and the bounded semantic disposition is ready for return
to Universal Ingestion. It grants no authority for:

- Extract Metadata or any Metadata schema;
- Create Manifest, Manifest schema, or Manifest persistence;
- Registry runtime or Registry objects;
- Process runtime or Event Engine behavior;
- Route runtime or AIOS Core behavior;
- response or acknowledgement delivery generation;
- Brain, Specialist Router, or Specialists;
- source, configuration, test, migration, runtime, deployment, commit, or merge.

Work must also stop on any missing mapping, inferred representation, inferred
path, lifecycle reorder, overwrite request, existing-file mutation, new
dependency, new canonical object, or conflict with Published and Active higher
authority.

## 5. Final Authority Assessment and Decision

The proposed extension is internally complete for the requested Stage 3.2.1
authority subjects and remains subordinate to every Published and Active parent
authority. It closes storage mapping, disposition, link representation,
filename, collision, overwrite, non-migration, existing-file, success, failure,
compatibility, dependency, runtime, and stop-boundary gaps without granting
implementation authority.

**FINAL ASSESSMENT: REVIEWED — PASS; AWAITING PROJECT OWNER APPROVAL**

**PROPOSED FINAL DECISION: APPROVE THIS SCOPED AUTHORITY EXTENSION AS A
GOVERNANCE-ONLY EXTENSION; REQUIRE DISTINCT REVIEW, APPROVAL, PUBLICATION, AND
ACTIVATION RECORDS BEFORE IT HAS AUTHORITY EFFECT.**
