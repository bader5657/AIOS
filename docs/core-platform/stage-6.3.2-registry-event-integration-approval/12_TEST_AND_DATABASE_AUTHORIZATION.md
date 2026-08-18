# Test and Database Authorization

Unit tests must cover Registry failure/no-event zero calls; one-event success;
exact envelope construction; unchanged DomainEvent/envelope; all bounded result
mappings; exactly one Process call; direct await; and no retry/rollback.

The focused integration test must exercise real Registry commit followed by an
injected DomainEvent, envelope construction, Event Engine, and a test-local
async handler. It must also prove Registry-row and upstream-artifact
preservation after Event Engine failure.

Disposable PostgreSQL is authorized using only
`AIOS_REGISTRY_TEST_DATABASE_URL` and the existing unchanged migration.
Production credentials, fallback, migration, and execution are prohibited.
