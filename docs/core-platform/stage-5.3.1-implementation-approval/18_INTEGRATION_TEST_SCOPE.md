# Exact Integration Test Scope

`test_registry_migrations.py` covers migration apply, exact catalog shape,
types/nullability, identity primary key, JSONB constraints, absence of binary,
unauthorized uniqueness/indexes/foreign keys, disposable down, and re-apply.

`test_postgres_registry.py` covers successful register, generated `record_id`,
metadata/relationships round trips, optional values, read happy/not-found,
allowed update, immutable preservation, update not-found, basic transaction
rollback evidence achievable without claiming the Stage 5.3.2 matrix, and no
original content.

Both require `AIOS_REGISTRY_TEST_DATABASE_URL`. When absent they explicitly
skip via the existing unittest convention and never fall back to another DSN.
