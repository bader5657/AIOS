# Static and Prohibited-Source Gates

Future source/path audits must prove:

- no BYTEA/BLOB/base64/original body persistence;
- no Registry Entry or historical Registry restoration;
- no SQLAlchemy, asyncpg, pool, migration framework, or extra dependency;
- no automatic retry;
- no delete, upsert, merge, or dedupe;
- no secondary index/extra uniqueness/foreign key/extension;
- no production credential/default DSN;
- no Asset Pipeline, Universal Ingestion, Manifest runtime, Telegram, Docker,
  or deployment modification; and
- no Stage 5.4.1 wiring.

Every changed path must be one of the eleven exact authorized paths.
