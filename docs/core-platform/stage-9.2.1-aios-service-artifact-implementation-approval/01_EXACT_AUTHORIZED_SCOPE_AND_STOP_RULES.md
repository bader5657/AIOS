# Exact Authorized Scope and Stop Rules

Future Stage 9.2.1 implementation is limited to:

1. `deploy/systemd/aios.service`
2. `tests/unit/core_platform/test_aios_systemd_service.py`

The test is required as a durable static contract gate for exact directives, one ExecStart, secret/test-DSN exclusion, migration prohibition, Docker ownership exclusion, and single-polling topology. No package marker or third path is required.

Any runtime Python, configuration, Docker/Compose, PostgreSQL, migration, dependency, installation helper, additional test/documentation, `/etc/systemd/system`, or VPS path requires separate scope approval. If the approved unit cannot invoke the current module without Python/PYTHONPATH changes, implementation must stop with `STAGE 9.2.1 RUNTIME CORRECTION APPROVAL REQUIRED`.
