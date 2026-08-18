# Event Engine Config Disposition Matrix

`config/event-engine.schema.json` remains unchanged and is classified as
**NON-AUTHORITATIVE CONFIGURATION / ADAPTABLE EVIDENCE**. Despite its filename,
it is not the active Event Engine runtime contract established by this package.

| Config claim | Stage 6.1.1 disposition |
|---|---|
| `engine: "AIOS Event Engine"` | Name aligns with Blueprint; no runtime semantics follow |
| `schema_version: "1.0"` | Config value only; not the canonical envelope integer field contract |
| Listed event names | Evidence only; does not authorize domain events or subscriptions |
| `mode: "publish_subscribe"` | Rejected as current authority; dispatch model deferred |
| `retry: true` | Rejected as current authority; retry not authorized |
| `max_retry: 3` | Rejected as current authority; no retry count approved |
| Brain/Specialist/Memory/business consumers | Rejected as current authority; later-layer behavior prohibited |
| Any implied delivery guarantee | Rejected; all guarantees unresolved/deferred |

This governance disposition neither edits nor activates the config artifact.
Future use requires explicit later authority and consistency with the active
DomainEvent/EventEnvelope boundary.
