# Immutability and Payload Boundary

Route preserves EventEnvelope and its DomainEvent unchanged. The runtime may
use only type identity and the minimum existing structural boundary required by
this contract.

It does not infer business meaning, classify intent, parse arbitrary payload,
choose a specialist, enrich the event, or mutate any canonical object. A valid
EventEnvelope requires no payload-dependent routing inspection in v1.
