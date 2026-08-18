# Exact Authorized Paths

Runtime—exactly one file:

- `core/ingestion/universal_ingestion.py`

Unit tests—exactly two files:

- `tests/unit/core_platform/test_universal_ingestion.py`
- `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`

Integration test—exactly one file:

- `tests/integration/registry/test_registry_event_engine_integration.py`

No fifth path is authorized. In particular, Event Engine, Registry, Domain
Foundation, Asset Pipeline, Document Manifest, migration, config, requirement,
and adapter files must not change.
