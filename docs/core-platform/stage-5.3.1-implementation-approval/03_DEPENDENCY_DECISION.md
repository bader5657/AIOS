# PostgreSQL Dependency Decision

**Approved dependency:** `psycopg[binary]==3.3.4`

**Approved approach:** Psycopg 3 asynchronous API with direct parameterized
SQL and no ORM.

The pinned binary extra is compatible with the inspected CPython 3.12 runtime,
avoids local compilation, and supports the async runtime boundary. Only
`requirements.txt` may change, with exactly this addition and no unrelated
upgrade.

Explicitly prohibited: SQLAlchemy, asyncpg, `psycopg_pool`, a migration
framework, another database abstraction, or another PostgreSQL client.
