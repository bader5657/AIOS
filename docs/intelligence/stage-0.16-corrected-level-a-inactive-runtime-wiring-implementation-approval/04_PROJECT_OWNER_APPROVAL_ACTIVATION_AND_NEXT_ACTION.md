# Project Owner Approval, Activation, and Next Action

I, as Project Owner, authorize the corrected Level A inactive Stage 0.16
Core-to-Brain runtime wiring implementation.

An explicit Level A attempt begins only when synthetic `brain_semantic_data` is
supplied. Exactly one correlation ID is then generated before EventEnvelope
construction and preserved through any later eligible Brain continuation.

Core routing independently determines Brain eligibility. Non-Brain routes may
retain the originating correlation ID but must not invoke the Mapper or Brain
boundary and must not generate a Brain request ID.

Default/current production behavior remains unchanged when Level A semantic
data and dependencies are absent.

AIOSCore, EventEnvelope schema, RequestContext, provider/runtime configuration,
production startup, schema binding, composition, production inference, Memory,
Specialist routing, business action, retry, fallback, and persistence remain
unchanged or unauthorized.

Activation of this governance package authorizes a future implementation branch
only after publication to `main`; it does not activate wiring or inference.
Level B and Level C remain unauthorized. The next official action is to
implement exactly the four approved paths, execute the complete non-live
verification matrix, and return retained evidence for final review.
