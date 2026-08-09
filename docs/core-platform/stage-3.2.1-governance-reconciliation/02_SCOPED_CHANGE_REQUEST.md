# Stage 3.2.1 Scoped Change Request

| Control | Value |
|---|---|
| Lifecycle | **PROPOSED** |
| Accepted baseline | `0091561d26342e9551d1470c6014bb47cb015fc8` |
| Target branch | `main` |
| Scope | Stage 3.2.1 storage-path contract implementation only |

## Exact Allowed Source Files

1. `core/storage/file_storage.py`
2. `core/storage/telegram_storage.py`
3. `core/ingestion/universal_ingestion.py`

## Exact Allowed Test Files

1. `tests/unit/core_platform/test_storage_path_contract.py`
2. `tests/unit/core_platform/test_universal_ingestion.py`
3. `tests/unit/core_platform/test_ingestion_capability_matrix.py`
4. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`

Every other source and test path is forbidden. In particular, Metadata,
Manifest schema, PostgreSQL, Registry, Event Engine, AIOS Core, Brain,
Specialists, adapters, classifiers, configuration, dependencies, deployment,
migration, Blueprint, Frozen Roadmap, Execution Plan, Authority Hierarchy,
Canonical Model, and Layer Architecture are excluded.

## Requested Change

Implement only the active mapping, original-filename separation, UUID v4
stored filename, collision failure, never-overwrite, no-retry, URL-only link,
Manifest path boundary, bounded persistence disposition, and stop-before-
Metadata contracts. Storage remains persistence owner. No public schema,
canonical object, layer, dependency, service, or later-stage behavior is added.

## Runtime Safety

Implementation and verification must not scan, list, read, write, rename, move,
copy, delete, reconcile, backfill, or migrate existing `/opt/aios/data`
content. Tests use synthetic temporary directories only. Production data,
secrets, services, Registry, Event Engine, AIOS Core, Brain, Specialist Router,
and Specialists must not be accessed or executed.

## Stop Conditions

Stop on baseline or ancestry mismatch; non-allowed path; contract ambiguity;
runtime-data contact; architecture, authority, schema, dependency, deployment,
or lifecycle expansion; overwrite; automatic rename; retry; rollback;
transaction logic; downstream continuation after Store Original failure; or
failed verification.
