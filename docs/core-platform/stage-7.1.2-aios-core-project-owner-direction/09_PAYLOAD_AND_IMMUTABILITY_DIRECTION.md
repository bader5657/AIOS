# Payload and Immutability Direction

AIOS Core may inspect only minimum EventEnvelope identity/metadata needed to
validate the Stage 7 Route boundary. It must not infer business meaning,
classify user intent, perform semantic reasoning, select specialists, or alter
the DomainEvent or EventEnvelope.

Payload-dependent routing is not authorized. Stage 7.2.1 must define the exact
minimum validation surface without widening event semantics.
