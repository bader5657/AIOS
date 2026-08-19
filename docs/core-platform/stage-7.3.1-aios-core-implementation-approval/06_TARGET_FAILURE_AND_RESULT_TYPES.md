# Target, Failure, and Result Types

The complete target set is:

```python
class CoreRouteTarget(str, Enum):
    AIOS_BRAIN_BOUNDARY = "aios_brain_boundary"
```

The complete failure-code set is:

```python
class CoreRouteFailureCode(str, Enum):
    INVALID_INPUT = "invalid_input"
```

The runtime-local, non-canonical result is exactly:

```python
@dataclass(frozen=True, slots=True)
class CoreRouteResult:
    success: bool
    route_target: CoreRouteTarget | None
    failure_code: CoreRouteFailureCode | None
    failure_reason: str | None
```

No second target, `UNSUPPORTED_INPUT`, fifth field, event, payload, decision
metadata, Brain response, retry count, timestamp, trace, or Registry ID is
authorized.
