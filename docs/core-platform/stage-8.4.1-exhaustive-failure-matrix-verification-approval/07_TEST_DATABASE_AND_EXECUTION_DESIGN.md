# Test, Database, and Execution Design

The authorized test is:

`tests/integration/core_platform/test_stage8_failure_matrix.py`

It should use compact parametrization where useful while retaining explicit
scenario-specific preservation assertions. It must use current Universal
Ingestion, Asset Pipeline, Registry, Event Engine, and AIOS Core where the
failure being proven requires them, with narrow test-local failure injection at
the authoritative owner boundary.

Real disposable PostgreSQL is authorized only through:

`AIOS_REGISTRY_TEST_DATABASE_URL`

Requirements are an isolated disposable database/schema/container, unchanged
existing migrations, no production fallback or credentials, and cleanup after
verification. Production DB use is prohibited.

Real Telegram is not required. External application network access, Telegram
API calls, and remote URL retrieval are prohibited. Local disposable PostgreSQL
connectivity is the only authorized external execution. No Brain runtime or
new infrastructure may be introduced.
