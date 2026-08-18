# Required Verification Matrix

| Scenario | Expected Registry outcome | Database state | Storage/Manifest | Retry |
|---|---|---|---|---|
| Actual isolation | Reports `READ COMMITTED` | Unchanged | None | None |
| Committed register | Row returned and later readable | Fully committed | None | None |
| Uncommitted update/read | Reader sees last committed value | Dirty state hidden | None | None |
| Later read after commit | Reader sees new value | Commit visible | None | None |
| Register write failure | `RegistryPersistenceError` | No partial row | None | None |
| Read missing | `None` | Unchanged | None | None |
| Read DB failure | `RegistryPersistenceError` | Unchanged | None | None |
| Update missing | `None` | Unchanged | None | None |
| Empty update | `ValueError` before connect | Unchanged | None | None |
| Multi-field update failure | `RegistryPersistenceError` | Prior row intact | None | None |
| Operation after rollback | Succeeds independently | Clean transaction | None | None |
| Unavailable endpoint | `RegistryPersistenceError` once | No connection/state | None | None |
| Boundary audit | No forbidden API/call | Unchanged | Ownership preserved | None |

Closure also requires Stage 5.3.1, Core Platform, Pipeline, and Domain
regressions; compile/static, dependency, binary-exclusion, prohibited-source,
test-DSN-only, and closed-world path audits.
