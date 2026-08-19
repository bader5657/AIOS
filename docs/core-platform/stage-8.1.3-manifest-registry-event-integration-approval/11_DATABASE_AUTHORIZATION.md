# Disposable PostgreSQL Authorization

Real disposable PostgreSQL execution is approved for test-only Stage 8.1.3
evidence. It is required to prove that the Registry commit is visible before the
test Event Engine handler runs.

Tests must use only `AIOS_REGISTRY_TEST_DATABASE_URL`, an isolated disposable
schema/container/environment, and the existing migration applied unchanged.

Production `AIOS_REGISTRY_DATABASE_URL`, production databases, production
fallback, committed credentials, and unrelated external network access are
prohibited. The disposable database reuses existing test capability and is not new
infrastructure.
