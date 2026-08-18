# Input Contract

The sole semantic input to AIOS Core Route is the existing immutable Domain
Foundation `EventEnvelope`.

AIOS Core consumes it directly. It must not modify the envelope or DomainEvent,
reconstruct a DomainEvent, enrich payload, reinterpret domain semantics, or
introduce a Core-specific input DTO. Registry rows/connections, Storage,
Manifest, wholesale Request Context, business aggregates, and Specialist data
are not Route inputs.
