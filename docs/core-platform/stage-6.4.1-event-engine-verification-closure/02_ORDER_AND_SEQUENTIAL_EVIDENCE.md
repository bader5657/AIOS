# Order and Sequential Evidence

Focused tests register A, B, then C and prove one explicit Process invocation
produces `A-start → A-end → B-start → B-end → C-start → C-end`. Async yield
points and start-time assertions prove each handler completes before the next
starts.

This is instance-local and invocation-local ordering only. No global,
distributed, durable, or broker ordering claim exists.
