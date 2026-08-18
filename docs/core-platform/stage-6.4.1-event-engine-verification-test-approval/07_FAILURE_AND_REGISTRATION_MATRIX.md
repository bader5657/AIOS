# Failure and Registration Matrix

| Condition | Required evidence |
|---|---|
| Invalid input | `success=False`, count 0, `INVALID_ENVELOPE`, zero handler calls, no retry |
| No matching handler | `success=False`, count 0, `NO_HANDLER`, no silent success, no retry |
| A succeeds, B raises, C remains | `HANDLER_FAILURE`, count 1, C not invoked, no retry or compensation |
| Invalid registration | `EventEngineRegistrationError` API exception |

A registration error is not an EventDelivery failure disposition. The delivery
failure-code set remains exactly `INVALID_ENVELOPE`, `NO_HANDLER`, and
`HANDLER_FAILURE`; no fourth code is authorized.
