# Supported Input and Validation

Every valid `EventEnvelope` presented after the successful Event Engine gate is
supported and routes to `AIOS_BRAIN_BOUNDARY`. No event-name whitelist or
alternative positive target exists.

Route validates only `isinstance(envelope, EventEnvelope)`. Domain Foundation
already owns envelope/event construction invariants. Core does not revalidate
business semantics, classify payload, inspect intent, or create a narrower
semantic eligibility rule.
