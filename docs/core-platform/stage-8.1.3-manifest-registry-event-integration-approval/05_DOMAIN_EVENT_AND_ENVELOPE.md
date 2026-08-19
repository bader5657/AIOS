# DomainEvent and EventEnvelope Contract

Only a caller-supplied, already-approved `DomainEvent` may be published. The count
is zero or one. No event may be synthesized from a Registry row, record ID,
Manifest, metadata, storage path, source URL, or RequestContext.

Universal Ingestion remains the EventEnvelope construction owner. Mapping is:

- `event` is the exact caller-supplied DomainEvent;
- `event_id`, `event_name`, and `occurred_at` mirror that event through the active
  Domain Foundation contract;
- `aggregate_id = None`;
- `correlation_id = None`;
- `causation_id = None`;
- `schema_version` is the exact caller-supplied value.

Registry `record_id` must not enter the EventEnvelope. Domain Foundation and the
EventEnvelope contract remain unchanged.
