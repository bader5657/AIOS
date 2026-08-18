# Proven and Untested Historical Behavior

## Proven by source and tests

- `Event` accepts string annotations for ID/name and a mutable dictionary
  payload; the dataclass is not frozen.
- default `created_at` is generated with timezone-naive `datetime.utcnow()`.
- blank ID/name strings raise built-in `ValueError`; tests cover empty strings.
- Registry appends handlers under an event-name key.
- `get_handlers()` returns a new list and returns `[]` for an unknown name.
- Dispatcher obtains that list and calls handlers sequentially in list order.
- one registered handler receives the exact same historical `Event` object.
- an unknown event causes zero handler calls and returns normally.
- dispatch and handlers are synchronous; `dispatch()` returns `None`.

## Assumed or untested

- whitespace-only validation is apparent from `.strip()` but untested.
- registration-order behavior follows append/iteration but multiple handlers
  and ordering are untested.
- duplicate handler registration, removal, concurrent mutation, and thread
  safety are unspecified and untested.
- handler exceptions propagate by ordinary Python behavior, but no failure
  contract or isolation test exists.
- payload mutation, validation, copying, and ownership are unspecified.
- retry, acknowledgement, idempotency, delivery guarantees, persistence,
  batching, correlation, causation, schema version, and downstream integration
  do not exist and are untested.

Absent behavior is not authority and cannot be promoted into a later contract.
