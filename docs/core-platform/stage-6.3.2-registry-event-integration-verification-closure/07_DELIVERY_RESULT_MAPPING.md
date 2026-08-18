# EventDeliveryResult Mapping Evidence

The lifecycle projection is exact:

| Event Engine result | Attempted | Succeeded | Failure code |
|---|---:|---:|---|
| Success | `True` | `True` | `None` |
| `INVALID_ENVELOPE` | `True` | `False` | `INVALID_ENVELOPE` |
| `NO_HANDLER` | `True` | `False` | `NO_HANDLER` |
| `HANDLER_FAILURE` | `True` | `False` | `HANDLER_FAILURE` |

No fourth delivery failure code or full `EventDeliveryResult` exposure was
introduced.
