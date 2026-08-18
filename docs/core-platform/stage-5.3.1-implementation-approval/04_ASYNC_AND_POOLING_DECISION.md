# Async and Pooling Decision

Use `psycopg.AsyncConnection` and async cursor/execute behavior. Registry owns
connection and transaction handling internally and exposes no Psycopg object.

No connection pool is authorized. Each scoped Registry operation obtains and
closes a connection through the approved boundary. `psycopg_pool` must not be
installed or imported.

Pooling, connection reuse, and load optimization remain future evidence-driven
decisions.
