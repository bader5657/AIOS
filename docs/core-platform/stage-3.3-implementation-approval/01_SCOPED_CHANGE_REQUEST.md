# Stage 3.3 Scoped Change Request

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Baseline | `3167ca3f2a0eefbd109f984f696b7cd58665a62a` |
| Objective | Implement the minimum active metadata contract at the bounded `Extract Metadata` lifecycle step |
| Change classification | Source and tests in a future separate implementation task |

## Exact Allowed Source Targets

1. `core/storage/metadata_engine.py`
2. `core/ingestion/universal_ingestion.py`

## Exact Allowed Test Targets

1. `tests/unit/core_platform/test_metadata_engine.py` (new)
2. `tests/unit/core_platform/test_universal_ingestion.py`
3. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`
4. `tests/unit/core_platform/test_ingestion_capability_matrix.py`

Every other path is forbidden. In particular, implementation may not change
Storage mechanics, Document Manifest, Registry, schemas, configuration,
dependencies, adapters, classifiers, Blueprint, Frozen Roadmap, Execution Plan,
Authority Hierarchy, Canonical Model, Layer Architecture, Stage 3.2.1, Stage
3.2.2, Stage 3.3.1 governance, deployment, services, or production data.

## Approved Inputs

Exactly: Text, Image, Voice, Audio, Video, PDF, DOC/DOCX, Spreadsheet, Web Link,
and YouTube Link. Manifest is not an input or media type and
`media_type = manifest` is prohibited.
