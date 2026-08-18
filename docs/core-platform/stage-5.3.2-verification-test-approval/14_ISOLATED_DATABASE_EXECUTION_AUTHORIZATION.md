# Stage 5.3.2 Isolated Database Execution Authorization

After this package is Published and Active, Stage 5.3.2 evidence may use only
a newly disposable test/development PostgreSQL addressed exclusively through
`AIOS_REGISTRY_TEST_DATABASE_URL`.

Permitted operations:

- start a disposable PostgreSQL database/container;
- apply the accepted Stage 5.3.1 UP migration;
- create disposable schemas and records;
- insert, read, and update disposable rows;
- open bounded concurrent test connections;
- use test-only read-only transaction settings and empty search paths;
- exercise controlled rollback/failure cases; and
- remove all disposable schemas, data, containers, and volumes.

No valued/persistent data is permitted. The authorization expires with Stage
5.3.2 evidence collection and grants no deployment or standing DB authority.

`PRODUCTION DATABASE EXECUTION = PROHIBITED`

No production DSN, credential, connection, read, write, migration, inspection,
or cleanup is authorized.
