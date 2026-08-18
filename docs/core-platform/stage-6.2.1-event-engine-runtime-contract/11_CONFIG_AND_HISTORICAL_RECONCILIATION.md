# Config and Historical Reconciliation

`config/event-engine.schema.json` remains unchanged and
**NON-AUTHORITATIVE CONFIGURATION / ADAPTABLE EVIDENCE**.

Its listed consumers, event list, publish/subscribe mode, Brain/Specialist/
Memory/business names, `retry: true`, and `max_retry: 3` do not enable runtime
behavior. No auto-loading or configuration-driven handler import is approved.
A future compatibility decision must be separately authorized.

Stage 6.1.2 **REPLACE** remains controlling. A future implementation is fresh;
historical files are not restored, copied, or cherry-picked.

Conceptual evidence retained:

- separate Event Engine package;
- defensive handler snapshot; and
- deterministic registration order.

Prohibited return includes historical generic `Event`, old dispatcher/registry
API, mutable arbitrary payload, naive generated timestamp, sync-only API,
silent unknown event, and historical handler API.
