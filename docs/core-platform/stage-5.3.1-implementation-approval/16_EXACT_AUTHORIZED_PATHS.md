# Exact Closed-World Implementation Paths

Only these eleven paths are authorized for future Stage 5.3.1 implementation:

## Dependency

1. `requirements.txt`

## Runtime

2. `core/registry/__init__.py`
3. `core/registry/postgres_registry.py`

## Migration

4. `migrations/postgres/0001_create_registry_records.up.sql`
5. `migrations/postgres/0001_create_registry_records.down.sql`

## Unit tests

6. `tests/unit/registry/__init__.py`
7. `tests/unit/registry/test_postgres_registry.py`

## Integration tests

8. `tests/integration/__init__.py`
9. `tests/integration/registry/__init__.py`
10. `tests/integration/registry/test_registry_migrations.py`
11. `tests/integration/registry/test_postgres_registry.py`

No wildcard authority exists. A need for any other path stops implementation
and requires scope amendment. Docker/deployment and existing pipeline/ingestion
files are not authorized.
