# Focused Boundary Test Contract

The dedicated focused test must exercise current Universal Ingestion as caller,
the current Event Engine, and the current AIOS Core. It may bind accepted
upstream Stage 8.1.3 prerequisites and use test-local async Event Engine
handlers. It must not use a real Brain.

It must prove at minimum:

1. no DomainEvent produces Event Engine 0/Core 0;
2. each bounded Event Engine failure produces Core 0;
3. Event Engine success produces exactly one Core call;
4. the Event Engine and Core receive the exact same envelope object;
5. EventDeliveryResult is not passed to Core;
6. Core success produces `route_handoff_ready=True` and the sole target;
7. bounded Core failure produces `route_handoff_ready=False`;
8. unexpected Core exception propagates;
9. upstream artifacts and completed Event result are preserved;
10. there is no retry, duplicate route, transaction coupling, or Brain call;
11. EventEnvelope, DomainEvent, identifiers, timestamps, and payload are unchanged;
12. no Memory, Specialist, business, LLM, broker, persistence, or network behavior.

Stage 7 unit evidence remains primary for `INVALID_INPUT`; Stage 8.1.3 evidence
remains primary for real Registry commit visibility.
