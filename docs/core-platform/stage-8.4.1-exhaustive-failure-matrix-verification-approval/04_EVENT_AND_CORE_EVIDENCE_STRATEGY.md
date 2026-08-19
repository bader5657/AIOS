# Event and Core Evidence Strategy

## Event Engine

- `INVALID_ENVELOPE`: unchanged Stage 6 evidence is the primary semantic
  proof. The Stage 8.4.1 integration may inject a legitimate bounded
  `EventDeliveryResult` solely to prove Core-zero gating. It must not corrupt a
  conforming EventEnvelope.
- `NO_HANDLER`: prove committed Registry and artifacts remain, Core is zero,
  and `route_handoff_ready=False`.
- `HANDLER_FAILURE`: prove Core is zero, committed state remains, and earlier
  handler effects are not compensated.
- Unexpected exception: prove propagation after Registry commit, Core zero,
  preservation, and no acknowledgement because ingestion does not return.

## AIOS Core

- A test-local Core-compatible bounded non-success result may be injected
  without corrupting same-envelope validity. It must produce
  `route_handoff_ready=False` after exactly one Core call.
- An unexpected Core exception must propagate after completed Event processing,
  with no false readiness or acknowledgement.
- Core failure must not alter the completed `EventDeliveryResult`.

The endpoint remains `AIOS_BRAIN_BOUNDARY` readiness. Brain invocation is
exactly zero.
