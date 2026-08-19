# Route Behavior Evidence

Every valid `EventEnvelope` deterministically returns:

```text
success=True
route_target=AIOS_BRAIN_BOUNDARY
failure_code=None
failure_reason=None
```

Every non-`EventEnvelope` returns, without normal public exception leakage:

```text
success=False
route_target=None
failure_code=INVALID_INPUT
failure_reason="route input must be an EventEnvelope"
```

Source and test inspection prove there is no event-name whitelist, payload
branching, semantic classification, alternate route, or unsupported-input
semantics.
