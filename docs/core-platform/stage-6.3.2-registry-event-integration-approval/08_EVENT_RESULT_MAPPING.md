# Event Result Mapping

| Event Engine result | Integration result |
|---|---|
| Success | attempted `True`; succeeded `True`; failure code `None` |
| `INVALID_ENVELOPE` | attempted `True`; succeeded `False`; same failure code |
| `NO_HANDLER` | attempted `True`; succeeded `False`; same failure code |
| `HANDLER_FAILURE` | attempted `True`; succeeded `False`; same failure code |

`INVALID_ENVELOPE` is mapped defensively if returned by the injected boundary;
the integration must not corrupt or fabricate an envelope to produce it. No new
Event Engine code or failure code is authorized.
