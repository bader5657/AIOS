# Retry Absence

`NO AUTOMATIC RETRY` applies to invalid envelope, no handler, handler failure,
Registry failure, and integration delivery failure. There is no loop, backoff,
retry count, maximum, reconnect-and-retry, fallback publication, or implicit
second Process call.

A later explicit caller invocation is a new invocation, not retry.
