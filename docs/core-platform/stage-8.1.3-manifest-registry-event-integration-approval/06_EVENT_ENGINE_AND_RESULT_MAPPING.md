# Event Engine Invocation and Result Mapping

Universal Ingestion may call `await EventEngine.process(envelope)` only after:

1. Manifest success;
2. Registry commit success;
3. an approved DomainEvent exists; and
4. valid EventEnvelope construction.

There is exactly one process call per publication attempt, with no task spawning
or retry.

The existing result projection is preserved:

| EventDeliveryResult | attempted | succeeded | failure code |
| --- | --- | --- | --- |
| success | `True` | `True` | `None` |
| `INVALID_ENVELOPE` | `True` | `False` | unchanged |
| `NO_HANDLER` | `True` | `False` | unchanged |
| `HANDLER_FAILURE` | `True` | `False` | unchanged |

No additional failure code is authorized.
