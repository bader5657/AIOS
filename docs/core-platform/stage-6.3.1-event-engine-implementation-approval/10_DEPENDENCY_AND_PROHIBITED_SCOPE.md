# Dependency and Prohibited Scope

Allowed dependencies are Python standard library and the active
`core.domain.event_envelope.EventEnvelope` contract. A direct DomainEvent import
is permitted only if concrete typing evidence requires it; implementation
should otherwise rely on the envelope.

Required direction:

`core/event → core/domain`

Forbidden:

- any `core/domain/` or Domain Foundation test change;
- Registry/PostgreSQL, Storage, Metadata, Manifest, Pipeline, Ingestion, Stage
  5, filesystem event history, cache, event log, outbox, or inbox dependency;
- Redis, Kafka, RabbitMQ, NATS, Celery, Dramatiq, RQ, HTTP/WebSocket event
  transport, broker, network client, or third-party package;
- retry loops/counters/backoff/config activation;
- Brain, Memory, Specialist Router, Specialist, or business consumer; and
- publisher/integration wiring reserved for Stage 6.3.2.

No new dependency or requirements-file change is authorized.
