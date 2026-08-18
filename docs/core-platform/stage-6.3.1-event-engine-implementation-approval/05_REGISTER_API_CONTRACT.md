# Register API Contract

Approved API:

```python
def register(self, event_name: str, handler: EventHandler) -> None: ...
```

Registration is synchronous, explicit, in-memory, and instance-local.
`event_name` must be a nonblank string and is preserved unchanged; handler must
be callable. Invalid registration raises the small runtime-local
`EventEngineRegistrationError` already approved by Stage 6.2.1.

Each valid registration appends one handler entry in registration order.
Ordinary repeated list registration is not deduplicated and establishes no
event duplicate/idempotency policy. No unregister, config subscription,
persistent registration, consumer group, or dynamic import is authorized.
