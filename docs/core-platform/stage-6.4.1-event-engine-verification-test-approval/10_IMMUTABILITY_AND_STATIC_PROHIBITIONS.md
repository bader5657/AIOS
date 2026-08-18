# Immutability and Static Prohibitions

Tests must prove Event Engine-owned behavior does not mutate the supplied
EventEnvelope or DomainEvent and preserves the active immutable contracts.
Domain Foundation remains unchanged.

Static audit must prove absence of gather, `create_task`, TaskGroup, worker
pool, fan-out, retry machinery, Registry/PostgreSQL persistence, event store,
outbox/inbox, filesystem queue, Redis, Kafka, RabbitMQ, NATS, Celery, network
delivery, and historical Event/dispatcher APIs.
