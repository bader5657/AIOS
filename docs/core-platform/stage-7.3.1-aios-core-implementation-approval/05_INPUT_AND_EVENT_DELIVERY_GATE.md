# Input and Event Delivery Gate

The sole Route input is the existing immutable
`core.domain.event_envelope.EventEnvelope`, consumed directly.

Successful Event Engine delivery is an external prerequisite enforced by the
caller/integration boundary. `EventDeliveryResult`, `EventDeliveryFailureCode`,
and Event Engine runtime types are not Route inputs, dependencies, or routing
semantics.

AIOS Core must not mutate or reconstruct the EventEnvelope or its contained
DomainEvent. Domain Foundation requires no change.
