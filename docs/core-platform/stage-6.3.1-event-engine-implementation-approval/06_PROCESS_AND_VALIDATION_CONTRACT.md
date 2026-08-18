# Process and Envelope Validation Contract

Approved API:

```python
async def process(
    self,
    envelope: EventEnvelope,
) -> EventDeliveryResult: ...
```

Python type annotations do not prevent runtime callers from supplying another
object. Process therefore performs the minimum boundary check:

- a non-`EventEnvelope` input returns `INVALID_ENVELOPE`;
- no handler is invoked; and
- no public historical `ValueError` is raised for that bounded case.

For an `EventEnvelope`, Domain Foundation already guarantees canonical event,
mirrored fields, timezone-aware occurrence time, and schema version. Event
Engine must not duplicate or reinterpret those semantics. It reads only the
exact `envelope.event_name` routing identity and preserves envelope/event
unchanged. Corrupted internal state or unrelated engine programming errors are
not silently converted into success.
