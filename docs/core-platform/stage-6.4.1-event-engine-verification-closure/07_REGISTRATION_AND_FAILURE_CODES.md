# Registration and Failure-Code Evidence

Invalid registration inputs continue to raise the Event Engine-local
`EventEngineRegistrationError`, a `ValueError` API validation exception rather
than an EventDelivery disposition.

The complete delivery failure-code set remains exactly
`INVALID_ENVELOPE`, `NO_HANDLER`, and `HANDLER_FAILURE`. No fourth code exists.
