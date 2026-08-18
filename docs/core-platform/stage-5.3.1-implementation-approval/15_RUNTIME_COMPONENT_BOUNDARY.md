# Runtime Component Boundary

Create a new current-authority `core/registry/` package. Reuse of the directory
name is not restoration of historical implementation.

`PostgresRegistry` owns only:

- narrow environment/DSN connection boundary;
- Psycopg async connection use;
- parameterized SQL;
- `register`, `read`, and `update`; and
- Registry-local transactions/errors.

It does not own Storage, metadata extraction, Manifest creation, Asset
Pipeline, business semantics, Registry Entry, pooling, migration execution,
caller integration, deployment, or production connection.

Historical `models.py`, `registry.py`, and pass-through `Registry.save()` must
not return.
