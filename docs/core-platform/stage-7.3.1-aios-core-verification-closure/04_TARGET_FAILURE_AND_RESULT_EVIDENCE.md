# Target, Failure, and Result Evidence

`CoreRouteTarget` contains exactly one member:

- `AIOS_BRAIN_BOUNDARY = "aios_brain_boundary"`

`CoreRouteFailureCode` contains exactly one member:

- `INVALID_INPUT = "invalid_input"`

`CoreRouteResult` is runtime-local, non-canonical, frozen, slotted, and contains
exactly `success`, `route_target`, `failure_code`, and `failure_reason`. There is
no second target, `UNSUPPORTED_INPUT`, additional failure taxonomy, or result
metadata.
