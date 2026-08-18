# Persistence, Broker, and Dependency Boundary

Event Engine v1 has **no persistence** and **no broker or durable queue**. It
must not create an event log, outbox, inbox, audit table, PostgreSQL event
table, filesystem queue, or persistent registration.

No Redis, Kafka, RabbitMQ, NATS, Celery, Dramatiq, RQ, background-worker
platform, or external network/broker client is authorized.

Future runtime may depend only on:

- active `DomainEvent`/`EventEnvelope` contracts;
- Python standard library; and
- minimal Event Engine-local result/error conventions approved here.

It must not depend on PostgreSQL/Registry internals, Storage, Metadata,
Document Manifest, Asset Pipeline, Universal Ingestion ownership, Brain,
Specialist Router, Specialists, or business features. No transaction spans
handler calls, Registry, publisher, or upstream artifacts.
