# Stage 3.2.1 Scoped Implementation Approval

| Control | Value |
|---|---|
| Lifecycle | **PROPOSED** |
| Exact stage | Stage 3 → Main Step 3.2 → Sub Step 3.2.1 |
| Accepted baseline commit | `0091561d26342e9551d1470c6014bb47cb015fc8` |
| Target branch | `main` |
| Implementation authority | **NONE until Approved, Published, and Active** |

## Approved Contract Subject

The requested future implementation authority is limited to the exact active
Stage 3.2.1 storage-path contract and the reviewed scoped filename/collision
mechanics. The substantive contract is not changed by baseline reconciliation.

## Closed-World Allowed Files

Source:

1. `core/storage/file_storage.py`
2. `core/storage/telegram_storage.py`
3. `core/ingestion/universal_ingestion.py`

Tests:

1. `tests/unit/core_platform/test_storage_path_contract.py`
2. `tests/unit/core_platform/test_universal_ingestion.py`
3. `tests/unit/core_platform/test_ingestion_capability_matrix.py`
4. `tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py`

All other repository files are forbidden implementation targets.

## Explicit Boundaries

- No production or existing runtime-data access or mutation.
- Do not run Registry, Event Engine, AIOS Core, Brain, Specialist Router, or
  Specialist runtime.
- Do not change Blueprint, Frozen Roadmap, Execution Plan, Authority Hierarchy,
  Canonical Model, Layer Architecture, Metadata, Manifest schema, database,
  configuration, deployment, services, dependencies, or public schemas.
- Do not create an ADR, authority class, canonical object, layer, dependency,
  migration, reconciliation, rollback framework, transaction, retry, or
  compensation mechanism.
- Preserve Stage 3.1.3 and Stage 3.1.4 behavior and lifecycle order.

## Acceptance Criteria

All explicit mappings and Manifest boundary are proven; original filename is
preserved separately and never used as the stored name; stored filename is a
single UUID v4 plus approved extension; collision fails once without overwrite,
rename, or retry; non-migration and runtime exclusion are proven; bounded
success/failure and all-or-nothing request disposition are preserved; any Store
Original failure stops before every downstream lifecycle owner; only allowed
files change; and all mandatory verification passes.

## Mandatory Verification

```text
python -m py_compile core/storage/file_storage.py core/storage/telegram_storage.py core/ingestion/universal_ingestion.py
python -m pytest -q tests/unit/core_platform/test_storage_path_contract.py tests/unit/core_platform/test_universal_ingestion.py tests/unit/core_platform/test_ingestion_capability_matrix.py tests/unit/core_platform/test_ingestion_lifecycle_boundaries.py
python -m pytest -q tests/unit/core_platform
python -m pytest -q
git diff --check
git diff --name-only
```

## Stop Conditions

Any failed authority, ancestry, scope, safety, compatibility, runtime,
dependency, test, or diff gate immediately removes readiness. No later stage is
authorized.
