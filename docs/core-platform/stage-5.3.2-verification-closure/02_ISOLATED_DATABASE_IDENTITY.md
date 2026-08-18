# Isolated Database Identity and Cleanup

Evidence used a new disposable `postgres:17-alpine` container:

| Item | Observed value |
|---|---|
| PostgreSQL version | `17.10` |
| Database | `aios_registry_stage532_test` |
| User | `aios_registry_stage532_test` |
| Host exposure | `127.0.0.1:55432` only |
| Network | default isolated Docker bridge; not `aios-net` |
| Storage | fresh anonymous disposable volume |
| Initial table | `registry_records` absent |
| Initial isolation | `read committed` |

`AIOS_REGISTRY_DATABASE_URL` was unset. Test processes received only
`AIOS_REGISTRY_TEST_DATABASE_URL`. The existing `aios-postgres` container
remained healthy and untouched.

After evidence collection the disposable container and anonymous volume were
removed.
