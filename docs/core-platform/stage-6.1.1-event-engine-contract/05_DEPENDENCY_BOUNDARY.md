# Dependency Boundary

The only authorized conceptual direction is:

`Integration/Application publisher → Event Engine → AIOS Core boundary`

Event Engine may consume the active `DomainEvent` and `EventEnvelope` contracts
without owning or modifying Domain Foundation. Sequential placement after
Registry does not authorize Registry internals as an Event Engine dependency.

Stage 6.1.1 prohibits Event Engine ownership of, or dependency used to acquire
ownership over:

- Storage, Metadata, or Document Manifest semantics;
- Universal Ingestion or Asset Pipeline lifecycle ownership;
- PostgreSQL Registry persistence internals or connection objects;
- business-domain logic;
- Brain, Intelligence, Specialist Router, Specialists, or concrete AIOS Core
  consumers;
- a network broker, external service, or durable queue.

No reverse dependency into Domain Foundation, Registry, ingestion, pipeline,
or artifact components is created. No Stage 5 file or contract changes.
