# Dependency Boundary

Allowed future runtime dependencies are limited to:

- `core.domain.event_envelope.EventEnvelope`;
- Python standard library `dataclasses` and `enum`;
- AIOS Core-local result and enum types.

No dependency on Registry/PostgreSQL, Event Engine implementation or result
types, Brain, Memory, Specialist Router, business features, Storage, Metadata,
Manifest internals, external services, or infrastructure is allowed.
