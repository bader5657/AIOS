# EventDeliveryResult Contract

`EventDeliveryResult` is a non-canonical, runtime-only immutable transport
representation. Repository conventions support a frozen, slotted dataclass.

Approved fields:

| Field | Contract |
|---|---|
| `success: bool` | Overall bounded Process outcome |
| `delivered_handler_count: int` | Number of handlers that completed successfully; nonnegative |
| `failure_code: EventDeliveryFailureCode | None` | Required on failure; absent on success |
| `failure_reason: str | None` | Required nonblank bounded text on failure; absent on success |

Approved runtime-local `StrEnum` members and values are:

- `INVALID_ENVELOPE = "invalid_envelope"` — boundary input is not a valid compatible EventEnvelope;
- `NO_HANDLER = "no_handler"` — no registration matches exact `event_name`; and
- `HANDLER_FAILURE = "handler_failure"` — an invoked handler raised before completing.

Success requires at least one handler and all attempted handlers to complete;
its count is therefore at least one. On handler failure, the count includes
only handlers completed before the failing handler, not the failing handler.
The result contains no exception object, traceback, retry count, queue offset,
broker ID, persistence ID, or acknowledgement token.

The enum/result exact implementation location is deferred to the closed
Stage 6.3.1 path approval; it must remain Event Engine-local.
