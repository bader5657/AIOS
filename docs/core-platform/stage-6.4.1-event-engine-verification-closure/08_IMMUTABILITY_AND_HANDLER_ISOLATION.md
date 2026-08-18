# Immutability and Handler Isolation

Tests prove Event Engine-owned behavior preserves the same immutable
EventEnvelope and DomainEvent objects and their state.

Handler isolation is limited to defensive snapshots, sequential awaited
execution, failure-stop containment, immutable event boundary, absence of
parallel shared tasks, and independent later invocations. No process, thread,
sandbox, or transactional handler isolation is claimed.
