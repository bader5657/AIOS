# Publication, Activation, and Implementation Gate

## Publication and activation

This governance package is published and active when its governance-only pull
request is merged to `main`. Activation authorizes the single legacy test path
addition recorded in this package and nothing else.

## Final authorized implementation paths

Runtime:

- `core/ingestion/universal_ingestion.py`

Tests:

- `tests/integration/core_platform/test_event_engine_aios_core_boundary_integration.py`
- `tests/integration/core_platform/test_document_manifest_registry_event_engine_integration.py`
- `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`
- `tests/unit/core_platform/test_universal_ingestion.py`
- `tests/integration/registry/test_registry_event_engine_integration.py`

The implementation gate requires authority-relevant failures to be zero, the
known eleven capability-matrix subfailures to remain separately classified if
unchanged, and the final implementation diff to contain no seventh path.

No later Stage 8 work is activated by this record.
