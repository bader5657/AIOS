# CoreRouteResult Contract

`CoreRouteResult` is a frozen, slotted, runtime-local, non-canonical dataclass:

```python
@dataclass(frozen=True, slots=True)
class CoreRouteResult:
    success: bool
    route_target: CoreRouteTarget | None
    failure_code: CoreRouteFailureCode | None
    failure_reason: str | None
```

Success is exactly `(True, AIOS_BRAIN_BOUNDARY, None, None)`. Failure is exactly
`(False, None, INVALID_INPUT, "route input must be an EventEnvelope")`.
No unrelated field or canonical-domain status is created.
