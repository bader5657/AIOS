# Route API

The approved conceptual API is:

```python
class AIOSCore:
    async def route(self, envelope: EventEnvelope) -> CoreRouteResult: ...
```

`Route` remains the authoritative lifecycle action. The API is async-only,
stateless, direct, and awaited. No sync API, background task, task spawning,
dispatch/process/execute alias, Brain call, or implementation is authorized.
