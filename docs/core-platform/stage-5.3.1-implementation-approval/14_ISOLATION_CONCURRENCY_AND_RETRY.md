# Isolation, Concurrency, and Retry

Use PostgreSQL `READ COMMITTED`. Do not add version columns, optimistic locks,
`SELECT FOR UPDATE`, application locks, `SERIALIZABLE`, retry-on-conflict, or
other concurrency policy.

Automatic retry is prohibited. No hidden retry loop, backoff, or retry count
may appear.

Comprehensive isolation, concurrency, and failure verification belongs to
Stage 5.3.2 and cannot be claimed by Stage 5.3.1.
