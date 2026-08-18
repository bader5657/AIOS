# Handler Failure and Recovery

For A succeeds, B raises, C would succeed, tests prove A and B run, C does not,
`HANDLER_FAILURE` is returned, and completed count is exactly one. A's visible
completed effect remains; no compensation or rollback is attempted.

A separate later Process invocation proves the EventEngine instance remains
usable and all three handlers can complete when the failure condition clears.
This is invocation-local recovery, not automatic retry.
