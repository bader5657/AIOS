# Stage 6.2.1 Deferral Matrix

| Question | Stage 6.1.1 disposition |
|---|---|
| Sync versus async execution | **DEFERRED TO STAGE 6.2.1** |
| Dispatch loop or behavior | **DEFERRED TO STAGE 6.2.1** |
| Concrete publisher implementation module | **DEFERRED TO STAGE 6.2.1** |
| Handler/subscriber API and concrete contract | **DEFERRED TO STAGE 6.2.1** |
| Subscriber registration and event-name mapping | **DEFERRED TO STAGE 6.2.1** |
| Retry and failure routing | **NOT AUTHORIZED; DEFERRED TO STAGE 6.2.1** |
| Unknown-event behavior | **DEFERRED TO STAGE 6.2.1** |
| Duplicate handling and idempotency | **DEFERRED TO STAGE 6.2.1** |
| At-most-/at-least-/exactly-once | **UNRESOLVED; DEFERRED** |
| Ordering guarantee | **UNRESOLVED; DEFERRED** |
| Acknowledgement and durable delivery | **UNRESOLVED; DEFERRED** |
| Concurrency and handler isolation | **DEFERRED TO STAGE 6.2.1** |
| Broker/queue choice, if ever needed | **NONE REQUIRED; any later choice needs authority** |
| Concrete runtime success/failure representation | **DEFERRED if implementation needs more detail** |

No implementation may infer an answer from historical code or current config.
Dead-letter handling, compensation, partial subscriber failure, broker offsets,
duplicate suppression, and durable delivery are likewise not established.
