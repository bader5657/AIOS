# Runtime API and Model

The only public runtime class and method are:

```python
class AIOSCore:
    async def route(self, envelope: EventEnvelope) -> CoreRouteResult: ...
```

The runtime is async-only, direct, stateless, deterministic, in-process, and
requires no mutable routing state. No `process`, `dispatch`, `execute`,
`reason`, `route_to_specialist`, `invoke_brain`, sync wrapper, background task,
worker, `create_task`, or `gather` API is authorized.

`core/aios_core/__init__.py` may expose only `AIOSCore`, `CoreRouteTarget`,
`CoreRouteFailureCode`, and `CoreRouteResult`.
