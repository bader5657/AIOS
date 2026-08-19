# DomainEvent, EventEnvelope, and Result Evidence

Only the exact caller-supplied, already-approved `DomainEvent` was accepted.
The focused evidence found no event synthesis from Registry record, record ID,
Manifest, metadata, storage path, source URL, or RequestContext.

When `domain_event is None`, registration remained successful and committed,
`EventEngine.process()` received zero calls, `event_publication_attempted` was
`False`, `event_delivery_succeeded` was `False`, and failure code was `None`.
This was correctly treated as a successful no-publication path.

For a supplied event, exactly one EventEnvelope was constructed and exactly one
`EventEngine.process()` call occurred. Mapping was exact:

- `event` is the supplied object;
- `event_id`, `event_name`, and `occurred_at` mirror that event;
- `aggregate_id`, `correlation_id`, and `causation_id` are `None`; and
- `schema_version` is the exact caller-supplied value.

Registry `record_id` did not enter the EventEnvelope. There was no second call,
fallback call, batching, retry, or background task.

Result projection remained unchanged:

| Event Engine disposition | attempted | succeeded | failure code |
|---|---:|---:|---|
| success | `True` | `True` | `None` |
| `INVALID_ENVELOPE` | `True` | `False` | unchanged |
| `NO_HANDLER` | `True` | `False` | `NO_HANDLER` |
| `HANDLER_FAILURE` | `True` | `False` | `HANDLER_FAILURE` |

Primary `INVALID_ENVELOPE` authority is the unchanged Stage 6 regression
`tests/unit/event/test_event_engine.py::EventEngineTests::test_invalid_envelope_returns_bounded_failure_without_handler`.
Unchanged Universal Ingestion unit evidence also verifies projection without
manufacturing invalid state in the conforming end-to-end flow.
