# Stage 3.4.1 Scoped Change Request

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Exact baseline | `773fc37d01e5205138d91a325fd510c975b80862` |
| Objective | Reconcile Document Manifest runtime, normative schema, ingestion handoff, and focused tests to the active Stage 3.4.1 authority |
| Implementation timing | Future separate implementation task only |

## Exact Closed-World Authorized Paths

### Runtime

1. `core/storage/document_manifest.py`
2. `core/ingestion/universal_ingestion.py`

### Normative schema

3. `config/ingestion-manifest.schema.json`

### Tests

4. `tests/unit/core_platform/test_document_manifest.py` (new)
5. `tests/unit/core_platform/test_universal_ingestion.py`
6. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`
7. `tests/unit/core_platform/test_ingestion_capability_matrix.py`

Every other path is forbidden. `test_storage_path_contract.py` is required
regression evidence but is not an authorized edit target because reuse of the
accepted Manifest storage boundary is already testable without changing it.
If any other path becomes necessary, stop and obtain a new Project Owner scope
expansion decision before editing it.

## Prohibited Scope

No Stage 3.2.x, Stage 3.3/3.3.1, Stage 3.4.1 authority, Blueprint, Frozen
Roadmap, architecture, Registry, dependency, adapter, classifier, storage-root
contract, production data, deployment/service, unrelated code/test, Stage 3.5,
or later-stage change is authorized. No production-data access, migration,
service activation, or network retrieval is authorized.
