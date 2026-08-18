# Route Target Contract

The runtime-local target representation is:

```python
class CoreRouteTarget(str, Enum):
    AIOS_BRAIN_BOUNDARY = "aios_brain_boundary"
```

This is the complete Stage 7 positive target set. The value means eligible for
future handoff at the named boundary; it is not a Brain instance or invocation.
No Specialist, Memory, Tool, Business, Content, Model, or Provider target exists.
