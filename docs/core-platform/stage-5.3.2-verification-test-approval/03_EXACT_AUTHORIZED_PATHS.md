# Exact Authorized Test Paths

Only these two paths may change during future Stage 5.3.2 verification:

- `tests/integration/registry/test_postgres_registry_isolation.py`;
- `tests/integration/registry/test_postgres_registry_failures.py`.

No existing test helper, runtime, migration, dependency, configuration, Docker,
deployment, or governance file is authorized for that future implementation.
Local helpers must remain inside the two approved test files.

If a third path is required, work stops for scope expansion approval.
