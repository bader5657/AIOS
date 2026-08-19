# Runtime API and Input Evidence

The fresh runtime exposes `AIOSCore` with exactly one public runtime operation:

```python
async def route(self, envelope: EventEnvelope) -> CoreRouteResult: ...
```

The input is only the existing immutable
`core.domain.event_envelope.EventEnvelope`. No AIOS-Core-specific semantic DTO,
Event Delivery result, Registry result, Request Context, Manifest, or business
DTO is accepted. There is no sync wrapper or second public runtime method.
