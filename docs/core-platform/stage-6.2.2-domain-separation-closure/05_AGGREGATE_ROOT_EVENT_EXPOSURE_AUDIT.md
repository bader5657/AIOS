# AggregateRoot Event Exposure Audit

The complete accepted Event Exposure API remains:

- `record_event(event: DomainEvent) -> None`
- `pending_events() -> tuple[DomainEvent, ...]`
- `pull_events() -> tuple[DomainEvent, ...]`
- `clear_events() -> None`

Pending events remain private, preserve insertion order, and are exposed as
immutable tuple snapshots. Equal and duplicate DomainEvent instances remain
valid domain exposure behavior.

AggregateRoot does not construct or store EventEnvelope, invoke Event Engine,
register handlers, publish/dispatch, retry, persist events, or own a broker.
Envelope construction remains solely outside AggregateRoot at the approved
Integration/Application publisher boundary.

**AGGREGATE ROOT / EVENT EXPOSURE SEPARATION = PASS**
