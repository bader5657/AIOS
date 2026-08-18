# Defensive Snapshot

Matching registrations are snapshotted before the first handler invocation. A
handler registered during current dispatch is excluded from that invocation
and becomes eligible for a later explicit Process invocation.

The later invocation is independent. Snapshot behavior creates no unregister,
dynamic subscription, persistent registry, or concurrency semantics.
