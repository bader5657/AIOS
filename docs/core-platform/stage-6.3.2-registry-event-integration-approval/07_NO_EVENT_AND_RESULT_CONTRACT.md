# No-Event and Lifecycle Result Contract

`IngestionResult` may receive exactly three backward-compatible fields:

```python
event_publication_attempted: bool = False
event_delivery_succeeded: bool = False
event_delivery_failure_code: EventDeliveryFailureCode | None = None
```

No DomainEvent after successful Registry commit produces `(False, False,
None)`. Registration remains successful and no Process call occurs. This is
not `NO_HANDLER` and is not an error.

The complete `EventDeliveryResult`, handler details, failure reason, and count
do not become the global ingestion result.
