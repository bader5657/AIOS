# Prohibited Scope

Stage 6.1.1 does not authorize:

- Event Engine runtime, event bus, dispatcher, handler registry, subscriber,
  publisher implementation, task queue, or workflow engine;
- Redis, Kafka, RabbitMQ, NATS, or any external/internal durable broker;
- event log, outbox, audit-event table, Event Engine database, PostgreSQL event
  table, serialization, or durable queue;
- retry, dead-letter, acknowledgement, delivery guarantees, ordering,
  duplicate handling, deduplication, or idempotency;
- changes to Domain Foundation, Stage 3/4/5, Registry, Universal Ingestion,
  Asset Pipeline, Document Manifest, Blueprint, Roadmap, architecture, config,
  runtime, tests, dependencies, schema, or migrations;
- AIOS Core runtime, Brain/Intelligence, Memory, Specialist Router,
  Specialists, Content Factory, business features, or production deployment;
- restoration or direct reuse of historical Event Engine code; or
- Stage 6.1.2, 6.2.1, or any later Stage 6 work.

Any such work requires its separately named authority and scope.
