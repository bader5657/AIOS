# Core Platform Stage 3.3.1 Draft

## Document Control

| Control | Value |
|---|---|
| Stage position | Stage 3 → Main Step 3.3 → Sub Step 3.3.1 |
| Official objective | Confirm required metadata per approved media/input class |
| Lifecycle state | **SUPERSEDED BY ACTIVE AUTHORITY PACKAGE** |
| Authority effect | **HISTORICAL RECONCILIATION RECORD ONLY** |
| Accepted baseline | `8ac29333d54bb499528154704bd4dcbd130a6da4` |
| Implementation status | **NOT AUTHORIZED; NOT STARTED** |

Repository presence does not make this document Approved, Published, Active,
or implementation authority. The exact accepted baseline above is the sole
baseline for this Stage 3.3.1 reconciliation.

## 1. Authority Basis and Method

This Draft uses Published and Active architecture, governance, Core Platform
authority, and the frozen execution order present in accepted history. Current
Python code, schemas, tests, runtime behavior, working-tree content, and common
practice do not supply missing authority and were not used to infer fields.

The Stage 3.3.1 contract must remain:

- minimum, business-first, and implementation-independent;
- limited to facts available at the bounded `Extract Metadata` step;
- free of network retrieval, rendering, content interpretation, enrichment,
  and guessed or synthetic values; and
- compatible with the official lifecycle and existing ownership boundaries.

## 2. Approved Media/Input Classes

Stage 3.3.1 covers exactly these Universal Ingestion classes:

1. Text
2. Image
3. Voice
4. Audio
5. Video
6. PDF
7. DOC/DOCX
8. Spreadsheet (`XLS`, `XLSX`, `CSV`, `ODS`)
9. Web Link
10. YouTube Link

Text is included as an approved input class. Manifest is not a media or input
class and must never be assigned `media_type = manifest`.

## 3. Lifecycle Boundary

The controlling order is preserved exactly:

```text
Store Original → Extract Metadata → Create Manifest → Register
```

Metadata extraction may begin only after successful original preservation.
Manifest creation occurs only after successful metadata extraction. A manifest
identifier or relationship may be attached by the later `Create Manifest`
boundary, but it is not extraction input, not an input-media field, and not a
condition of metadata-extraction success.

## 4. Requiredness Rule

A field may be Required only when its value is deterministically available
inside Stage 3.3.1 from the accepted input identity, the already-preserved
original, or the already-received URL. A field is Optional when it may be
absent, format-dependent, or unavailable without network retrieval, rendering,
content interpretation, enrichment, or guessing. Fields without a minimum v1
business need are omitted.

The proposed field-by-field contract is maintained in
`CORE_PLATFORM_STAGE_3_3_1_METADATA_AUTHORITY_PACKAGE.md`.

## 5. Explicit Exclusions

This Draft does not authorize implementation, tests, schemas, storage changes,
runtime actions, network access, parsing technology, persistence design,
manifest construction, Registry behavior, migration, or later-stage work. It
does not modify Stage 3.2.1, the Blueprint, the Frozen Roadmap, or any Active
architecture or governance document.

## 6. Approval Gate Resolution

The Project Owner confirmed:

- the exact baseline and the ten-class scope above;
- inclusion of Text and exclusion of Manifest as a media/input class;
- every Required and Optional field in the authority package;
- the deterministic-requiredness rule;
- the lifecycle and manifest-artifact boundary; and
- that approval of metadata authority does not authorize implementation.

## Draft Decision

Stage 3.3.1 was reconciled as a historical draft against accepted baseline
`8ac29333d54bb499528154704bd4dcbd130a6da4`.

**HISTORICAL DRAFT — SUPERSEDED. NO IMPLEMENTATION AUTHORIZED.**
