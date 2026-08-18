# EventEngine Injection and Call

The smallest explicit dependency is another backward-compatible keyword:

```python
event_engine: EventEngine | None = None
```

When `domain_event` is present for a publication-capable lifecycle,
`event_engine` must be supplied by the caller. Missing injection is a caller
contract error, not a delivery disposition. Universal Ingestion must not create
a global singleton or a fresh empty engine with no registered handlers.

After all gates pass, Universal Ingestion directly awaits exactly one
`event_engine.process(envelope)` call. There is no task creation, gather,
thread, queue, retry, fallback call, or distributed exactly-once guarantee.
