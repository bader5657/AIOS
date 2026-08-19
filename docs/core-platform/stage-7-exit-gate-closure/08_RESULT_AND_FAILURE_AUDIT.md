# CoreRouteResult and Failure Audit

`CoreRouteResult` is runtime-local, non-canonical, frozen, slotted, and contains
exactly `success`, `route_target`, `failure_code`, and `failure_reason`.

`CoreRouteFailureCode` contains exactly `INVALID_INPUT = "invalid_input"`.
`UNSUPPORTED_INPUT` and every additional speculative failure taxonomy remain
unauthorized and absent.

Valid input returns `(True, AIOS_BRAIN_BOUNDARY, None, None)`. Non-envelope
input returns `(False, None, INVALID_INPUT, "route input must be an
EventEnvelope")` without normal public exception leakage.
