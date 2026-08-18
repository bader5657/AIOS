# Async and Prohibited Capability Audit

The only invocation is the direct
`await event_engine.process(envelope)`. Source and dependency audits prove the
absence of `create_task`, gather, TaskGroup, background jobs, batching, retry,
broker/queue transport, event persistence, outbox/inbox, and distributed
transaction behavior.

No Brain, Memory, Specialist, AIOS Core consumer, or later Stage 6 capability
was introduced.
