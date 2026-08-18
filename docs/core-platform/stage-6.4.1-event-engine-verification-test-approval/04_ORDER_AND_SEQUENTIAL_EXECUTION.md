# Order and Sequential Execution

One EventEngine instance registering A, B, then C for one event name must, on
one explicit Process invocation, await A, then B, then C. A handler must finish
before the next starts.

This is deterministic registration order within one instance and one
invocation only. It creates no global, distributed, durable, cross-process, or
broker ordering guarantee. Parallel fan-out is prohibited.
