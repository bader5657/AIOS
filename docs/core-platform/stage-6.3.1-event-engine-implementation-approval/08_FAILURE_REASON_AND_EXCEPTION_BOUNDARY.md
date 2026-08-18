# Failure Reason and Exception Boundary

Approved deterministic reasons may be fixed runtime-local text:

- invalid input: `input must be an EventEnvelope`;
- no handler: `no handler registered for event_name`; and
- handler failure: text identifying that the handler failed and its exception
  class, without exception object, arbitrary traceback, or stack data.

An ordinary handler exception is translated to `HANDLER_FAILURE`; completed
count includes only earlier handlers, and remaining handlers are not invoked.
Cancellation and interpreter-control exceptions must not be swallowed.

No retry, compensation, rollback, or reversal of completed handler side
effects occurs. Unexpected engine-internal programming errors are not broadly
caught or silently translated.
