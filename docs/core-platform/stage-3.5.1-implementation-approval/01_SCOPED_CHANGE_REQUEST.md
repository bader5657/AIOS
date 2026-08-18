# Stage 3.5.1 Scoped Change Request

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Exact baseline | `ef55b65141773739360b3d5e942ef84c5603ce86` |
| Project Owner disposition | **REMOVE COUPLING** |
| Objective | Remove `core.storage.telegram_storage` → `core.app.input_classifier` while preserving accepted behavior |
| Implementation timing | Future separate implementation task only |

## Exact Closed-World Authorized Paths

### Runtime

1. `core/storage/telegram_storage.py`
2. `core/ingestion/universal_ingestion.py`

Repository inspection found no Adapter or other production caller of
`save_telegram_attachment()`. No additional runtime path is authorized.

### Tests

3. `tests/unit/core_platform/test_telegram_input_boundary.py`
4. `tests/unit/core_platform/test_universal_ingestion.py`
5. `tests/unit/core_platform/test_ingestion_capability_matrix.py`
6. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`

Every other path is forbidden. These unchanged files are mandatory regression
evidence but are not edit targets:

- `tests/unit/core_platform/test_storage_path_contract.py`;
- `tests/unit/core_platform/test_metadata_engine.py`;
- `tests/unit/core_platform/test_document_manifest.py`;
- all discovered Core Platform and domain tests.

If any other path becomes necessary, stop and return
`STAGE 3.5.1 SCOPE EXPANSION DECISION REQUIRED` before editing it.

## Prohibited Scope

No change is authorized to Stage 3.2.x, Stage 3.3/3.3.1, Stage 3.4.x, the
Stage 3.5.1 governance package, Blueprint, Frozen Roadmap, architecture or
domain documents, Registry, PostgreSQL, Manifest or metadata authority,
deployment/services, production data, Adapter, Stage 4, Stage 5, or unrelated
runtime/tests. No new dependency, shared enum/module, media type, classifier,
network behavior, lifecycle step, migration, or production-data operation is
authorized.
