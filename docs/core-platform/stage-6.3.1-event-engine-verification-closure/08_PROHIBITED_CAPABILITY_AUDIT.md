# Prohibited Capability Audit

Source inspection proves absence of retry/backoff, persistence, PostgreSQL,
Registry access, event log/store, outbox/inbox, filesystem persistence, broker,
queue, HTTP/WebSocket transport, and parallel handler execution.

Registry/publisher → Event Engine integration is absent and remains reserved for
Stage 6.3.2. Stage 5 is unchanged.
