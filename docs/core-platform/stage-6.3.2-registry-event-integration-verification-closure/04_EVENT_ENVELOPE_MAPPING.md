# EventEnvelope Mapping Evidence

Universal Ingestion constructs exactly one envelope only after Registry success
and only when the caller supplies a DomainEvent. The mapping is exact:

- `event` is the same supplied object;
- `event_id` mirrors `domain_event.id` through the Domain Foundation envelope;
- `event_name` and `occurred_at` mirror the supplied event;
- aggregate, correlation, and causation IDs are `None`; and
- schema version is the exact caller-supplied `event_schema_version`.

Registry `record_id` is not mapped. Identity and timestamp are not regenerated,
and the DomainEvent is not mutated.
