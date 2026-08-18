# Domain Foundation Separation Audit

Dependency direction is `core/event → core/domain`; reverse Event Engine imports
from Domain Foundation are absent. DomainEvent, EventEnvelope, and AggregateRoot
remain free of handler registration, dispatch, retry, persistence, broker,
delivery results, and Event Engine runtime ownership.

Domain Foundation source and contracts remain unchanged.
