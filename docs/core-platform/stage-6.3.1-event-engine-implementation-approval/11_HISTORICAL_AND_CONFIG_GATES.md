# Historical Replacement and Config Gates

Stage 6.1.2 REPLACE remains controlling. Implementation must be fresh and must
not restore, cherry-pick, copy, or recreate:

- historical generic Event or mutable payload contract;
- historical `event.py`, dispatcher, or registry API;
- naive `datetime.utcnow()` timestamp generation;
- synchronous-only dispatch;
- silent unknown-event success; or
- historical handler API/tests.

Conceptual defensive snapshot and registration-order ideas may be implemented
only as specified by current authority.

`config/event-engine.schema.json` remains unchanged and non-authoritative.
Runtime must not read it to enable retry, consumers, Brain, Specialist, Memory,
business handlers, publish/subscribe, or broker behavior.
