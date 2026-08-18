# Exact Unit Test Scope

`tests/unit/registry/test_postgres_registry.py` must cover:

- DTO/input boundary validation;
- parameterized SQL behavior where mockable;
- register result mapping and Registry-local errors;
- read not-found;
- update not-found;
- mutable versus immutable field surface;
- deterministic `ValueError` for empty update before connection;
- no delete/upsert/dedupe API;
- no Registry Entry;
- no retry/pool/ORM behavior; and
- configuration boundary/fail-closed missing environment behavior.

Tests use `unittest`/`IsolatedAsyncioTestCase` conventions already present.
