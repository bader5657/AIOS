# Payload Boundary Audit

AIOS Core performs only `EventEnvelope` boundary/type validation. It does not
interpret business payload, classify intent or user requests, select a
Specialist, branch on event names, transform an event, or alter payload values.

Route neither mutates nor reconstructs the `EventEnvelope` or its contained
`DomainEvent`; both retain identity and values after routing.
