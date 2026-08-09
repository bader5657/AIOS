# Stage 3.2.2 Scoped Change Request

| Control | Value |
|---|---|
| Lifecycle | **APPROVED** |
| Baseline | `79448eab8b343ee09b141bc73faeba767e6b92e4` |
| Requested future change | Bounded mixed/multiple-original storage barrier and verification only |

## Exact Allowed Source Targets

1. `core/storage/telegram_storage.py`
2. `core/ingestion/universal_ingestion.py`

## Exact Allowed Test Targets

1. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`
2. `tests/unit/core_platform/test_ingestion_capability_matrix.py`
3. `tests/unit/core_platform/test_universal_ingestion.py`

## Exact Forbidden Targets

Every other path is forbidden, including `core/storage/file_storage.py`, all
Metadata/Manifest/Registry/Event Engine/AIOS Core/Brain/Router/Specialist code,
adapters, classifiers, schemas, configuration, dependencies, deployment,
Blueprint, Frozen Roadmap, Execution Plan, Canonical Model, Authority Hierarchy,
Layer Architecture, and all tests not listed above.

The future change may only replace the single-attachment assumption with the
approved all-recognized-file-original barrier and add its verification. It may
not alter Stage 3.2.1 storage mechanics or implement Link, Manifest,
PostgreSQL, or downstream runtime.
