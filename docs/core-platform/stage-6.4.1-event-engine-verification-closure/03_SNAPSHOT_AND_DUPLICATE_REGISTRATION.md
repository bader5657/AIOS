# Snapshot and Duplicate-Registration Evidence

The defensive snapshot test proves a handler registered during current
dispatch is excluded from that invocation and eligible in a later explicit
invocation.

Registering the exact same callable twice produces two ordinary registration
entries and two calls in one invocation. No deduplication, rejection, or
handler-identity policy was added.
