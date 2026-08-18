# Routing, Process, and Result Audit

The only routing key is exact `EventEnvelope.event_name`. The runtime operation
is async `EventEngine.process(EventEnvelope) -> EventDeliveryResult`.

The delivery failure set is exactly `INVALID_ENVELOPE`, `NO_HANDLER`, and
`HANDLER_FAILURE`. `EventEngineRegistrationError` remains a local API validation
exception and is not a fourth delivery disposition.
