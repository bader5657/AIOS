# Failure Code Decision

The complete initial failure-code set is:

```python
class CoreRouteFailureCode(str, Enum):
    INVALID_INPUT = "invalid_input"
```

`INVALID_INPUT` means the supplied object is not an `EventEnvelope`. There is no
Brain, Router, Model, retry, persistence, or other failure code.

`UNSUPPORTED_INPUT` is not authorized because active authority supplies no
valid-but-unsupported EventEnvelope case. Retaining it would invent semantics.
