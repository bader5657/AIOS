# Historical Inventory

| Historical path | Proven role |
|---|---|
| `core/event/__init__.py` | Empty package marker |
| `core/event/event.py` | Slotted mutable dataclass `Event` |
| `core/event/registry.py` | In-memory event-name-to-handler list registry |
| `core/event/dispatcher.py` | Synchronous sequential handler loop |
| `tests/unit/event/__init__.py` | Empty test package marker |
| `tests/unit/event/test_event.py` | Construction and blank-string validation tests |
| `tests/unit/event/test_registry.py` | Registration and unknown-name lookup tests |
| `tests/unit/event/test_dispatcher.py` | One-handler delivery and silent unknown-event tests |

Public runtime surface:

- `Event(event_id, event_name, payload, created_at=datetime.utcnow())`;
- `EventRegistry.register(event_name, handler)`;
- `EventRegistry.get_handlers(event_name)`;
- `EventDispatcher(registry)`; and
- `EventDispatcher.dispatch(event) -> None`.

The source imports only Python standard library plus its own `core.event`
modules. Historical tests import `pytest`, although that commit's
`requirements.txt` does not pin pytest. There is no PostgreSQL, network,
broker, queue, EventEnvelope, Domain Foundation, or persistence dependency.
