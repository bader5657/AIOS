# Acceptance Criteria

Stage 7.3.1 later passes only if exactly the four authorized files implement and
test the active contract: a fresh `AIOSCore`, one async `route`, EventEnvelope
input, one Brain-boundary target, one invalid-input failure code, and the exact
four-field frozen/slotted result.

All valid envelopes must route identically without payload inspection. Invalid
objects must return the exact bounded failure. The implementation must be
stateless, deterministic, immutable with respect to Domain objects, and free of
integration, Brain, Memory, Specialist, business, persistence, retry,
broker/network, infrastructure, historical, and extra dependency semantics.

Every verification gate must pass. Implementation completion does not itself
close Stage 7 verification, begin Stage 7.3.2, or authorize Stage 8 integration.
