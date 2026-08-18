# Result and Failure Evidence

`EventDeliveryResult` is frozen, slotted, runtime-local, and contains exactly:
`success`, `delivered_handler_count`, `failure_code`, and `failure_reason`.

The complete delivery failure-code set is exactly:

1. `INVALID_ENVELOPE`
2. `NO_HANDLER`
3. `HANDLER_FAILURE`

`EventEngineRegistrationError` is solely the local registration validation
exception and is not a delivery disposition.
