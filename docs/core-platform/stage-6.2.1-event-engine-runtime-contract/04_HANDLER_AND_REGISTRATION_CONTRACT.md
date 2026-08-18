# Handler and Registration Contract

The minimum handler type is an in-process async callable equivalent to:

```python
EventHandler = Callable[[EventEnvelope], Awaitable[None]]
```

Handlers are runtime consumers, not domain objects. They receive the same
immutable envelope supplied to Process and must not be interpreted as
persistent/network subscribers.

Registration is a synchronous, explicit, in-memory operation equivalent to:

```python
register(event_name: str, handler: EventHandler) -> None
```

`event_name` uses the canonical routing vocabulary and must be a nonblank
string; the handler must be callable. Invalid registration is rejected through
a small Event Engine-local `EventEngineRegistrationError`, not a global error
taxonomy. Registration is retained only for the lifetime of that EventEngine
instance.

No database registration, config auto-loading, dynamic import string, Service
Locator, persistent subscription, consumer group, or acknowledgement offset is
authorized. Event duplicate/idempotency semantics are unrelated and remain
unauthorized; this package does not define duplicate registration behavior.
