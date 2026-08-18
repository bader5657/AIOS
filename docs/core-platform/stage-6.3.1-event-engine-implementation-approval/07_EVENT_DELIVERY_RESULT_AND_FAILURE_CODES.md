# EventDeliveryResult and Failure Codes

Implement `EventDeliveryResult` as a frozen, slotted, runtime-local,
non-canonical dataclass with exactly:

- `success: bool`
- `delivered_handler_count: int`
- `failure_code: EventDeliveryFailureCode | None`
- `failure_reason: str | None`

Implement `EventDeliveryFailureCode` as a runtime-local `StrEnum` with exactly:

- `INVALID_ENVELOPE = "invalid_envelope"`
- `NO_HANDLER = "no_handler"`
- `HANDLER_FAILURE = "handler_failure"`

No fourth code is authorized. Result invariants:

| Outcome | success | count | code | reason |
|---|---:|---:|---|---|
| all matched handlers complete | `True` | completed count ≥ 1 | `None` | `None` |
| invalid input | `False` | 0 | `INVALID_ENVELOPE` | bounded nonblank text |
| no matching handler | `False` | 0 | `NO_HANDLER` | bounded nonblank text |
| handler raises | `False` | earlier completed count | `HANDLER_FAILURE` | bounded nonblank text |

The DTO contains no exception object, traceback, retry count, broker token,
queue offset, acknowledgement, or persistence identifier.
