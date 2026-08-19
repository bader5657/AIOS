# Exact Route Behavior

Route performs only `EventEnvelope` type/boundary validation.

For every valid EventEnvelope after the external successful-delivery gate, it
returns exactly:

```python
CoreRouteResult(
    success=True,
    route_target=CoreRouteTarget.AIOS_BRAIN_BOUNDARY,
    failure_code=None,
    failure_reason=None,
)
```

For any supplied object that is not an EventEnvelope, it returns exactly:

```python
CoreRouteResult(
    success=False,
    route_target=None,
    failure_code=CoreRouteFailureCode.INVALID_INPUT,
    failure_reason="route input must be an EventEnvelope",
)
```

Every valid EventEnvelope is supported. There is no whitelist, event-name
routing table, payload inspection, semantic classification, or alternate route.
