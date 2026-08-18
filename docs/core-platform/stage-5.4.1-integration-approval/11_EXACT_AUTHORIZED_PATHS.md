# Exact Closed-World Implementation Paths

Only these four paths are authorized for future Stage 5.4.1 implementation:

## Runtime

1. `core/ingestion/universal_ingestion.py`

## Unit tests

2. `tests/unit/core_platform/test_universal_ingestion.py`
3. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`

## Integration test

4. `tests/integration/registry/test_manifest_registry_integration.py`

No wildcard authority exists. `core/registry/__init__.py` already exports the
required runtime types and is not authorized for change. A need for any other
runtime or test path stops work with `STAGE 5.4.1 SCOPE EXPANSION REQUIRED`.
