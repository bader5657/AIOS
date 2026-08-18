# Canonical Event and Envelope Contract

## DomainEvent

`DomainEvent` remains the canonical event concept: an abstract, immutable
domain record of a fact that occurred. Its supplied `id`, timezone-aware
`occurred_at`, and unchanged nonblank `event_name` remain governed by Domain
Foundation. The Event Engine neither creates nor replaces this model and does
not generate domain facts. The historical generic `Event` is obsolete and
non-authoritative.

## EventEnvelope

`EventEnvelope` is the immutable, transport-neutral wrapper used when one
already-approved `DomainEvent` crosses the Event Engine boundary. Exactly one
published DomainEvent is wrapped by one envelope for one Process invocation.
No batching or multi-event envelope is defined.

The complete active field set remains unchanged:

| Field | Existing authority |
|---|---|
| `event` | Required `DomainEvent`; preserved without mutation |
| `event_id` | Exact read-only mirror of `event.id`; not supplied or generated independently |
| `event_name` | Exact read-only mirror of `event.event_name`; not normalized |
| `occurred_at` | Exact read-only mirror of timezone-aware `event.occurred_at`; not generated |
| `aggregate_id` | Optional; may be `None`; no aggregate lookup |
| `correlation_id` | Optional; may be `None`; no automatic generation |
| `causation_id` | Optional; may be `None`; no automatic generation |
| `schema_version` | Required positive integer at least 1; preserved unchanged |

The envelope adds no payload field beyond the wrapped concrete DomainEvent.
Any domain payload belongs to that concrete event contract; this package does
not invent, flatten, serialize, or mutate it. EventEnvelope is not a domain
event, persistence record, broker message, or queue job.
