# No-Handler, Invalid-Input, and Handler-Failure Semantics

| Condition | Result | Count | Invocation behavior |
|---|---|---:|---|
| Invalid/non-envelope boundary input | failure / `INVALID_ENVELOPE` | 0 | invoke no handler |
| Valid envelope, zero matching handlers | failure / `NO_HANDLER` | 0 | do not silently succeed |
| Every matched handler completes | success | number completed | finish normally |
| A handler raises an ordinary exception | failure / `HANDLER_FAILURE` | number completed earlier | stop immediately |

Handler failure exposes bounded nonblank failure text through the result; it
does not expose the exception object as cross-boundary state. Remaining
handlers are not called. The engine does not retry, compensate completed
handlers, undo their side effects, or rollback Registry/upstream work.

Process catches only ordinary handler exceptions needed for this bounded
translation. Cancellation and interpreter-control exceptions are not silently
converted into success or swallowed. Invalid-envelope behavior is a result,
not the historical generic `ValueError` public contract.
