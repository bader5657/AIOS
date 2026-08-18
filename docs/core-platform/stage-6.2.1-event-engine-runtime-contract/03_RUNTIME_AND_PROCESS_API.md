# Runtime Model and Process API

The approved runtime model is **async, in-process, and in-memory**.

The exact v1 operation is conceptually:

```python
async def process(
    self,
    envelope: EventEnvelope,
) -> EventDeliveryResult: ...
```

`EventEngine.process()` owns one bounded Process invocation. There is no
parallel synchronous API and no historical `dispatch()`, `emit()`, or
`publish()` alias. A synchronous caller, if ever approved, adapts at its own
boundary rather than creating a second engine implementation.

The publisher remains outside Event Engine and supplies an already-constructed
envelope. Process returns only the runtime-local bounded result defined by this
package; it does not return a DomainEvent, EventEnvelope replacement, handler
receipt, broker token, or persistence record.
