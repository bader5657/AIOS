# Dependency and Prohibited Scope

The approved new dependency direction is bounded to Universal Ingestion
consuming the public DomainEvent/EventEnvelope and Event Engine APIs. Domain
Foundation never imports ingestion or Event Engine.

Prohibited scope includes synthetic events, Registry-derived event facts,
multiple events, Stage 6.3.1 modification, AIOS Core/Brain/Memory/Router/
Specialist consumers, business handlers, retry, persistence, broker, queue,
network transport, event store/outbox/inbox, deduplication, idempotency,
delivery guarantees, and new third-party dependencies.
