# Prohibited Capability Audit

Runtime source and AST/import audits prove absence of automatic retry, backoff,
retry counters, maximum retry, gather, task creation, TaskGroup, worker pool,
fan-out, Registry/PostgreSQL persistence, event store/log, outbox/inbox,
filesystem queue, Redis, Kafka, RabbitMQ, NATS, Celery, HTTP/WebSocket delivery,
and historical Event/dispatcher/registry APIs.

The fresh async in-memory runtime remains unchanged; historical REPLACE remains
controlling.
