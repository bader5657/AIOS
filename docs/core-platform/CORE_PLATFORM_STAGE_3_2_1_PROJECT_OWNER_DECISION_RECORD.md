# AIOS — Stage 3.2.1 Project Owner Decision Record

| Control | Value |
|---|---|
| Accepted authority baseline | `f4f49fd6df7535f409f9659edafcf5ed2d9f58a3` |
| Scope | Stage 3 → Main Step 3.2 → Sub Step 3.2.1 |
| Record class | Project Owner Decision |
| Decision status | **FINAL — APPROVED BY PROJECT OWNER INSTRUCTION** |
| Publication status | **PENDING ACCEPTANCE INTO REPOSITORY HISTORY** |
| Activation status | **NOT ACTIVE — PUBLICATION GATE NOT SATISFIED** |
| Implementation authority | **NONE** |

This record preserves the Project Owner decisions supplied for D01–D25. It
does not implement them. Under the Published and Active governance lifecycle,
creation of this working-tree record is not publication, and approval is not
activation. Publication requires acceptance into repository history; activation
may occur only after that publication gate is satisfied.

## Decisions

### D01 — Storage-Path Contract

- **Question:** Shall Stage 3.2.1 establish a complete storage-path contract?
- **Project Owner Decision:** **APPROVED.** Establish the complete contract using D02–D25.
- **Authority Basis:** The Blueprint requires `Store Original`; Execution Plan 3.2.1 requires a storage-path contract and migration/non-migration decision.
- **Reason:** Close the explicitly identified Stage 3.2.1 authority boundary without changing higher authority.
- **Stop Boundary:** No implementation or lifecycle advance follows from this decision record.
- **Impact:** Stage 3.2.1 authority content is decided, subject to publication and activation gates.
- **Implementation Authority:** **NONE.**

### D02 — Complete Storage-Class Mapping

- **Question:** Shall Stage 3.2.1 adopt a complete explicit storage-class mapping?
- **Project Owner Decision:** **APPROVED.** The complete mapping is D03–D12.
- **Authority Basis:** The Blueprint publishes the input scope and six storage roots but does not bind every class to a root.
- **Reason:** Eliminate implicit class-to-root selection.
- **Stop Boundary:** No class or root beyond the explicit decisions may be inferred.
- **Impact:** The mapping is complete at the authority-decision level.
- **Implementation Authority:** **NONE.**

### D03 — Image Mapping

- **Question:** Where shall original Image input be mapped?
- **Project Owner Decision:** **APPROVED:** `Image → /opt/aios/data/documents/images`.
- **Authority Basis:** Image and the `images` root are Published by the Blueprint.
- **Reason:** Establish their previously absent explicit binding.
- **Stop Boundary:** Image recognition and runtime behavior remain unchanged.
- **Impact:** Adds only the Stage 3.2.1 Image path decision.
- **Implementation Authority:** **NONE.**

### D04 — Voice Mapping

- **Question:** Where shall original Voice input be mapped?
- **Project Owner Decision:** **APPROVED:** `Voice → /opt/aios/data/documents/voice`.
- **Authority Basis:** Voice and the `voice` root are Published by the Blueprint.
- **Reason:** Establish their explicit binding.
- **Stop Boundary:** Voice recognition and runtime behavior remain unchanged.
- **Impact:** Adds only the Stage 3.2.1 Voice path decision.
- **Implementation Authority:** **NONE.**

### D05 — Audio Mapping

- **Question:** Where shall original Audio input be mapped?
- **Project Owner Decision:** **APPROVED:** `Audio → /opt/aios/data/documents/voice`.
- **Authority Basis:** Audio is canonical; Storage owns original Audio persistence; `voice` is a Published root. The binding is supplied by this Project Owner decision.
- **Reason:** Resolve the absent Audio path decision.
- **Stop Boundary:** Audio remains a distinct canonical input; it is not reclassified as Voice.
- **Impact:** Adds a storage-path binding only.
- **Implementation Authority:** **NONE.**

### D06 — Video Mapping

- **Question:** Where shall original Video input be mapped?
- **Project Owner Decision:** **APPROVED:** `Video → /opt/aios/data/documents/images`.
- **Authority Basis:** Video is canonical; Storage owns original Video persistence; `images` is a Published root. The binding is supplied by this Project Owner decision.
- **Reason:** Resolve the absent Video path decision.
- **Stop Boundary:** Video remains a distinct canonical input; it is not reclassified as Image.
- **Impact:** Adds a storage-path binding only.
- **Implementation Authority:** **NONE.**

### D07 — PDF Mapping

- **Question:** Where shall original PDF input be mapped?
- **Project Owner Decision:** **APPROVED:** `PDF → /opt/aios/data/documents/pdf`.
- **Authority Basis:** PDF and the `pdf` root are Published by the Blueprint.
- **Reason:** Establish their explicit binding.
- **Stop Boundary:** PDF recognition and processing remain unchanged.
- **Impact:** Adds only the PDF path decision.
- **Implementation Authority:** **NONE.**

### D08 — DOC/DOCX Mapping

- **Question:** Where shall original DOC and DOCX inputs be mapped?
- **Project Owner Decision:** **APPROVED:** `DOC, DOCX → /opt/aios/data/documents/docs`.
- **Authority Basis:** DOC/DOCX and the `docs` root are Published by the Blueprint.
- **Reason:** Establish one explicit document-root binding for both inputs.
- **Stop Boundary:** No other input class is included by implication.
- **Impact:** Adds only the DOC/DOCX path decision.
- **Implementation Authority:** **NONE.**

### D09 — Spreadsheet Mapping

- **Question:** Where shall original Spreadsheet input be mapped?
- **Project Owner Decision:** **APPROVED:** `Spreadsheet (XLS, XLSX, CSV, ODS) → /opt/aios/data/documents/docs`.
- **Authority Basis:** Spreadsheet and its accepted formats are canonical; `docs` is a Published root.
- **Reason:** Resolve the absent Spreadsheet path decision.
- **Stop Boundary:** Recognition formats, parsing, and processing are unchanged.
- **Impact:** Adds a storage-path binding only.
- **Implementation Authority:** **NONE.**

### D10 — Web Link Mapping

- **Question:** How shall Web Link be handled?
- **Project Owner Decision:** **APPROVED:** `Web Link → /opt/aios/data/documents/links`, represented as URL only. No file is created; no download, fetch, cache, or snapshot is permitted.
- **Authority Basis:** Web Link is canonical and `links` is a Published root; this decision supplies the previously absent representation contract.
- **Reason:** Preserve the canonical URL without introducing remote-content behavior.
- **Stop Boundary:** No dereference, normalization, retrieval, enrichment, cache, snapshot, or file representation.
- **Impact:** Adds a URL-only link-original boundary.
- **Implementation Authority:** **NONE.**

### D11 — YouTube Link Mapping

- **Question:** How shall YouTube Link be handled?
- **Project Owner Decision:** **APPROVED:** `YouTube Link → /opt/aios/data/documents/links`, represented as URL only under the same contract as Web Link.
- **Authority Basis:** YouTube Link is canonical and `links` is a Published root.
- **Reason:** Use one bounded URL-only preservation contract while retaining distinct canonical identity.
- **Stop Boundary:** No download, fetch, cache, snapshot, extraction, or host-recognition change.
- **Impact:** Adds a YouTube Link mapping and representation boundary only.
- **Implementation Authority:** **NONE.**

### D12 — Manifest Boundary

- **Question:** What Manifest handling belongs to Stage 3.2.1?
- **Project Owner Decision:** **APPROVED:** path boundary only at `/opt/aios/data/documents/manifests`.
- **Authority Basis:** The Blueprint publishes `manifests` and names `Create Manifest`.
- **Reason:** Preserve the storage boundary without expanding Manifest authority.
- **Stop Boundary:** No Manifest schema, Metadata, Registry, or Canonical Model change.
- **Impact:** Path-boundary clarification only.
- **Implementation Authority:** **NONE.**

### D13 — Original Filename Policy

- **Question:** How shall the original filename be treated?
- **Project Owner Decision:** **APPROVED:** preserve it separately as metadata; the storage filename need not match it.
- **Authority Basis:** Original preservation is Published; filename roles were previously undefined.
- **Reason:** Preserve source naming independently from storage naming.
- **Stop Boundary:** No metadata schema, sanitization algorithm, or normalization rule is created.
- **Impact:** Establishes the authority-level role of the original filename.
- **Implementation Authority:** **NONE.**

### D14 — Storage Filename Policy

- **Question:** What policy governs the storage filename?
- **Project Owner Decision:** **APPROVED:** use a unique filename and retain the original filename as metadata.
- **Authority Basis:** Storage owns original persistence; no prior filename mechanism was Published.
- **Reason:** Separate storage uniqueness from the received filename.
- **Stop Boundary:** No UUID, hash, timestamp, encoding, extension, or generation algorithm is authorized here.
- **Impact:** Establishes a uniqueness invariant only.
- **Implementation Authority:** **NONE.**

### D15 — Link-Original Representation

- **Question:** What is the original representation for Web Link and YouTube Link?
- **Project Owner Decision:** **APPROVED:** the canonical original is the URL; no file, download, or snapshot is created.
- **Authority Basis:** Web Link and YouTube Link canonical identities are URL-based.
- **Reason:** Preserve the canonical original without substituting remote content.
- **Stop Boundary:** No file format, schema, serialization, normalization, fetch, download, or snapshot.
- **Impact:** Resolves the link-original representation as URL only.
- **Implementation Authority:** **NONE.**

### D16 — Collision Policy

- **Question:** What happens when the target already exists?
- **Project Owner Decision:** **APPROVED:** fail; do not overwrite and do not rename automatically.
- **Authority Basis:** Store Original failure stops before Metadata; no overwrite authority exists.
- **Reason:** Prevent implicit mutation or naming behavior.
- **Stop Boundary:** No replacement, deduplication, equivalence inference, or automatic alternate name.
- **Impact:** Establishes a bounded collision-failure disposition.
- **Implementation Authority:** **NONE.**

### D17 — Overwrite Policy

- **Question:** May an existing artifact be overwritten?
- **Project Owner Decision:** **APPROVED:** **NEVER OVERWRITE**.
- **Authority Basis:** No Published destructive mutation authority exists.
- **Reason:** Protect existing artifacts and preserve the storage boundary.
- **Stop Boundary:** Any overwrite requirement requires separate Project Owner authority.
- **Impact:** Establishes an absolute non-overwrite invariant for Stage 3.2.1.
- **Implementation Authority:** **NONE.**

### D18 — Existing Runtime Files

- **Question:** How shall existing runtime files be treated?
- **Project Owner Decision:** **APPROVED:** **NO TOUCH**; no scan, rename, move, copy, delete, or migration.
- **Authority Basis:** Execution Plan 3.2.1 prohibits touching secrets or data without scoped authority.
- **Reason:** Preserve existing runtime state.
- **Stop Boundary:** No access to or mutation of existing runtime files.
- **Impact:** Establishes the existing-file safety boundary.
- **Implementation Authority:** **NONE.**

### D19 — Migration Policy

- **Question:** Does Stage 3.2.1 migrate existing data?
- **Project Owner Decision:** **APPROVED:** **NON-MIGRATION**; no old data is migrated.
- **Authority Basis:** Execution Plan 3.2.1 requires an explicit migration/non-migration decision.
- **Reason:** Keep existing state outside the Stage 3.2.1 change boundary.
- **Stop Boundary:** No backfill, conversion, relocation, reconciliation, or existing-state mutation.
- **Impact:** Resolves Stage 3.2.1 as non-migratory.
- **Implementation Authority:** **NONE.**

### D20 — Success Disposition

- **Question:** What may Storage return on success?
- **Project Owner Decision:** **APPROVED:** bounded success disposition only; no runtime response object.
- **Authority Basis:** Active Stage 3.1.4 authority permits only a bounded original-preservation disposition.
- **Reason:** Confirm success without expanding the runtime contract.
- **Stop Boundary:** No claim about Metadata or later lifecycle completion and no response-object design.
- **Impact:** Resolves semantic success at the Storage boundary.
- **Implementation Authority:** **NONE.**

### D21 — Failure Disposition

- **Question:** What may Storage return on failure?
- **Project Owner Decision:** **APPROVED:** bounded failure disposition; no retry, rollback, or compensation.
- **Authority Basis:** Active Stage 3.1.4 authority requires Store Original failure to stop before Metadata.
- **Reason:** Preserve the bounded failure boundary without new runtime behavior.
- **Stop Boundary:** Stop before Metadata; no retry, rollback, compensation, or error-object design.
- **Impact:** Resolves semantic storage failure.
- **Implementation Authority:** **NONE.**

### D22 — Partial Failure

- **Question:** What disposition applies when one part of a request fails?
- **Project Owner Decision:** **APPROVED:** **ALL OR NOTHING**; if one part fails, the request is considered failed.
- **Authority Basis:** Multiple inputs retain distinct identity; this Project Owner decision supplies the previously absent aggregate disposition.
- **Reason:** Establish one request-level success criterion.
- **Stop Boundary:** This semantic decision does not authorize rollback, compensation, transaction, algorithm, or runtime mechanics. Any implementation need for those mechanisms requires separate authority.
- **Impact:** Resolves the request-level partial-failure disposition only.
- **Implementation Authority:** **NONE.**

### D23 — Bounded Storage Output

- **Question:** What information may Storage return to Universal Ingestion?
- **Project Owner Decision:** **APPROVED:** semantic bounded disposition only; no new response object.
- **Authority Basis:** Active authority permits only a bounded persistence result.
- **Reason:** Prevent expansion into API or schema design.
- **Stop Boundary:** No fields, serialization, exception, protocol, or response-object definition.
- **Impact:** Resolves the authority-level output boundary.
- **Implementation Authority:** **NONE.**

### D24 — Exact Implementation Targets

- **Question:** Which exact files may a later implementation modify?
- **Project Owner Decision:** **APPROVED:** no files are selected in this package; exact-file decisions are deferred to the next Scoped Change Request.
- **Authority Basis:** The Execution Plan requires a scoped approved target list before implementation.
- **Reason:** Separate authority completion from implementation scoping.
- **Stop Boundary:** No file is authorized for modification by this record.
- **Impact:** Establishes the mandatory next governance gate; it does not create an implementation target list.
- **Implementation Authority:** **NONE.**

### D25 — Compatibility and Verification Targets

- **Question:** What invariants govern Stage 3.2.1 verification?
- **Project Owner Decision:** **APPROVED:** preserve all Published Stage 3.1.3 and Stage 3.1.4 invariants, and require explicit mappings, no inference, unchanged lifecycle, unchanged Canonical Model, unchanged Layer Architecture, Store Original failure stopping before Metadata, no new dependency, no new runtime, and no new canonical object.
- **Authority Basis:** Published Blueprint, Canonical Model, Layer Architecture, Core Platform Authority Decision, Stage 3.1.3 authority, and closed Stage 3.1.4 authority.
- **Reason:** Bind Stage 3.2.1 to all controlling compatibility boundaries.
- **Stop Boundary:** Any conflict, inference, missing mapping, lifecycle change, architecture change, dependency addition, runtime expansion, or canonical-object creation stops work.
- **Impact:** Establishes the formal verification target set.
- **Implementation Authority:** **NONE.**

## Final Authority Decision Summary

| Decision | Decision Status | Final Result |
|---|---|---|
| D01 | APPROVED | Complete storage-path contract |
| D02 | APPROVED | Complete explicit storage-class mapping |
| D03 | APPROVED | Image → `images` |
| D04 | APPROVED | Voice → `voice` |
| D05 | APPROVED | Audio → `voice` |
| D06 | APPROVED | Video → `images` |
| D07 | APPROVED | PDF → `pdf` |
| D08 | APPROVED | DOC/DOCX → `docs` |
| D09 | APPROVED | Spreadsheet → `docs` |
| D10 | APPROVED | Web Link → `links`; URL only |
| D11 | APPROVED | YouTube Link → `links`; URL only |
| D12 | APPROVED | Manifest path boundary only |
| D13 | APPROVED | Original filename preserved separately as metadata |
| D14 | APPROVED | Unique storage filename; mechanism unspecified |
| D15 | APPROVED | Link original is URL; no file |
| D16 | APPROVED | Collision fails; no overwrite or automatic rename |
| D17 | APPROVED | Never overwrite |
| D18 | APPROVED | Existing runtime files: no touch |
| D19 | APPROVED | Non-migration |
| D20 | APPROVED | Bounded semantic success disposition |
| D21 | APPROVED | Bounded semantic failure disposition |
| D22 | APPROVED | All-or-nothing request disposition |
| D23 | APPROVED | Semantic bounded output only |
| D24 | APPROVED | Exact files deferred to Scoped Change Request; no file authorized here |
| D25 | APPROVED | Published invariants plus explicit Stage 3.2.1 verification targets |

## Authority Activation

The Project Owner decisions D01–D25 are final and approved by the instruction
recorded in this document. They replace `UNRESOLVED`, `PROPOSAL ONLY`, and
`PROJECT OWNER DECISION REQUIRED` at the **decision** level only.

They are **not yet Published or Active authority**. Under the controlling
governance lifecycle, publication requires acceptance of this approved record
into repository history. Activation must be recorded after publication. This
document must not claim those gates were satisfied merely because a working-tree
file exists.

## Authority Scope

These decisions apply only to Stage 3, Main Step 3.2, Sub Step 3.2.1. They do
not change the Blueprint, Frozen Roadmap, Canonical Model, Layer Architecture,
Execution Plan, Registry runtime, Event Engine, Brain, Specialists, Pipeline,
Manifest schema, database, or runtime.

## Stop Condition

This document records Project Owner decisions only. It grants no implementation
approval. Publication and activation remain mandatory authority gates.
Implementation additionally requires a Scoped Change Request, Working Procedure,
exact implementation targets, Implementation Approval, Review, Acceptance, and
Governance Closure under the official lifecycle.

**PROJECT OWNER DECISIONS: FINAL — APPROVED**

**PUBLICATION: PENDING ACCEPTANCE INTO REPOSITORY HISTORY**

**ACTIVATION: NOT ACTIVE**

**IMPLEMENTATION AUTHORITY: NONE**
