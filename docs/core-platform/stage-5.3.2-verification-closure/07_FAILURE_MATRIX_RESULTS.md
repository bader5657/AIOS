# Failure Matrix Results

| Scenario | Result |
|---|---|
| Register persistence failure | Registry-local error; zero partial rows |
| Read missing | `None` |
| Read database failure | Registry-local error |
| Update missing | `None` |
| Empty update | `ValueError` before connection |
| Multi-field update failure | Registry-local error; complete prior row preserved |
| Unavailable loopback endpoint | Registry-local error within bounded time |
| Later operation after rollback | Successful |

Write failures used disposable PostgreSQL read-only transaction settings.
Read failure used a disposable empty search path. No schema was altered to
manufacture a failure.
