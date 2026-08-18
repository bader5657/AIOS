# Registry Injection and Configuration Boundary

The smallest approved mechanism is a keyword-only optional Registry dependency
on `ingest_telegram_message`, typed as `PostgresRegistry | None` or an exact
structural equivalent that does not create a new public framework.

- Tests inject a mock, fake, or explicitly constructed `PostgresRegistry`.
- When no dependency is injected, Universal Ingestion constructs
  `PostgresRegistry.from_environment()` only after successful Manifest/readiness
  validation and immediately before the single Register call.
- Runtime construction therefore uses only `AIOS_REGISTRY_DATABASE_URL`, as
  already owned by the Registry runtime.
- Integration verification constructs its Registry explicitly from
  `AIOS_REGISTRY_TEST_DATABASE_URL` and must never fall back to the runtime
  variable.

No global singleton, hard-coded DSN, credential, configuration framework,
Document Manifest construction, or Pipeline construction is authorized.
Existing exports in `core/registry/__init__.py` are sufficient; that file does
not require authorization.
