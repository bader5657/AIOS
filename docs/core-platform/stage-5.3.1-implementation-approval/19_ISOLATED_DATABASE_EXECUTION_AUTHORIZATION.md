# Isolated Test/Development PostgreSQL Execution Authorization

This record is distinct from code/dependency/migration approval even though it
is published in the same governance package.

**AUTHORIZED ENVIRONMENT:** isolated disposable test/development PostgreSQL
only, addressed exclusively through `AIOS_REGISTRY_TEST_DATABASE_URL`.

Future Stage 5.3.1 evidence may connect, apply the approved migration, inspect
schema, insert/read/update disposable records, exercise empty/disposable
reversal, re-apply, and clean disposable test schema/data.

Authorization is limited to the approved files, schema, operations, and tests.
It grants no standing authority outside Stage 5.3.1 evidence collection.
