# Isolated PostgreSQL Execution Authorization

Stage 5.4.1 verification is authorized only against a disposable
test/development PostgreSQL database addressed explicitly through
`AIOS_REGISTRY_TEST_DATABASE_URL`.

Authorized actions are:

1. create a temporary PostgreSQL container or database;
2. apply the existing Stage 5.3.1 migration UP without changing it;
3. execute end-to-end registration through Universal Ingestion;
4. inspect the disposable `registry_records` row;
5. execute controlled Registry failure scenarios; and
6. clean the disposable environment.

If the test variable is absent, integration verification must skip or fail
closed according to the focused test convention. It must never read or fall
back to `AIOS_REGISTRY_DATABASE_URL`. Production credentials, migration, data,
and execution remain prohibited.
