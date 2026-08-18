# Configuration Boundary

| Environment variable | Authorized use |
|---|---|
| `AIOS_REGISTRY_DATABASE_URL` | Future non-test Registry runtime DSN; production use remains separately prohibited |
| `AIOS_REGISTRY_TEST_DATABASE_URL` | Isolated automated/integration test and disposable development execution only |

The runtime package may provide a narrow environment-reading construction
boundary and otherwise hold the DSN privately. No credentials, password,
default DSN, `.env`, localhost guess, or broad configuration framework may be
committed.

Integration tests must require the test variable explicitly and must never
fall back to the runtime variable. Missing test DSN must cause an explicit
unittest skip, not a guessed connection.
