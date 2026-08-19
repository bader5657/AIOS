# Authority, Baseline, and Scope

The controlling records are the Stage 8.1.4 implementation approval published
through PR #63 and the narrow legacy-test scope correction published through PR
#64. Implementation PR #65 merged commit
`d47cf5844d761f42d1e9bbc3feff23fd5a7a506c` to `main`.

The accepted implementation contains exactly six paths:

- `core/ingestion/universal_ingestion.py`
- `tests/integration/core_platform/test_event_engine_aios_core_boundary_integration.py`
- `tests/integration/core_platform/test_document_manifest_registry_event_engine_integration.py`
- `tests/integration/registry/test_registry_event_engine_integration.py`
- `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`
- `tests/unit/core_platform/test_universal_ingestion.py`

Universal Ingestion is the sole integration caller. Event Engine, AIOS Core,
Registry, and Domain Foundation runtime contracts remain unchanged.
