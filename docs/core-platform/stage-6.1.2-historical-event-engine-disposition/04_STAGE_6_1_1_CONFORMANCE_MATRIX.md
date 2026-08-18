# Stage 6.1.1 Conformance Matrix

| Historical behavior/concept | Classification | Active-authority comparison |
|---|---|---|
| Separate `core/event/` component boundary | CONFORMS | Event Engine remains a distinct component outside Domain Foundation |
| Empty package marker | EVIDENCE ONLY | Carries no runtime contract |
| Generic historical `Event` | OBSOLETE | Cannot replace canonical `DomainEvent` |
| No `EventEnvelope` input | CONFLICTS | Active Process input is one already-constructed envelope |
| Mutable arbitrary payload dictionary | CONFLICTS | Bypasses concrete immutable DomainEvent semantics and envelope field boundary |
| Independently supplied `event_id`/`event_name` | CONFLICTS | Envelope mirrors canonical DomainEvent values |
| Generated `created_at=datetime.utcnow()` | CONFLICTS | Canonical occurrence time is supplied, timezone-aware, and mirrored unchanged |
| Built-in `ValueError` validation | CONFLICTS | Not the active Domain Foundation validation/boundary contract |
| Handler registry keyed by name | UNAUTHORIZED | Registration and subscriber API are deferred to Stage 6.2.1 |
| Synchronous sequential dispatch loop | UNAUTHORIZED | Dispatch and sync/async choice are deferred |
| Defensive copied handler list | ADAPTABLE | Useful later design evidence, not approved behavior |
| Registration-order iteration | ADAPTABLE | Useful later evidence; no ordering guarantee follows |
| Silent unknown-event success | UNAUTHORIZED | Cannot define Process success/failure; unknown dispatch semantics are deferred |
| `dispatch() -> None` | CONFLICTS | Does not provide bounded success/failure disposition |
| No retry/persistence/broker | CONFORMS | Stage 6.1.1 authorizes none; absence creates no future policy |
| No Brain/Specialist behavior | CONFORMS | Downstream remains AIOS Core boundary only |
| Seven narrow tests | EVIDENCE ONLY | Prove history, not active contract compliance |

The historical runtime does not implement active bounded `Process`; its
executable surface is either obsolete/conflicting or reserved for Stage 6.2.1.
