# Isolated Database Authorization

Disposable PostgreSQL execution is authorized only to rerun unchanged
Registry→Event Engine and Stage 5 regression evidence. Tests must use only
`AIOS_REGISTRY_TEST_DATABASE_URL`, unique disposable schemas, the existing
unchanged migration, and cleanup that drops each schema.

Production database execution is prohibited. There is no production fallback,
new migration, schema change, production credential use, or
`AIOS_REGISTRY_DATABASE_URL` authorization.
