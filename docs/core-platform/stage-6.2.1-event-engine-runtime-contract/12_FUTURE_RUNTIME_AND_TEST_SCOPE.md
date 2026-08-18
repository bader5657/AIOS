# Future Runtime and Test Scope

No runtime or test path is authorized for change by Stage 6.2.1. The smallest
preferred path set for a later Stage 6.3.1 implementation-approval audit is:

## Runtime candidates

- `core/event/__init__.py`
- `core/event/event_engine.py`

`event_engine.py` should contain the EventEngine, handler callable alias,
runtime-local registration error, failure-code enum, and EventDeliveryResult
unless the implementation-approval audit proves a separate file necessary.
Historical `event.py`, `registry.py`, and `dispatcher.py` are not authorized by
this package.

## Unit-test candidates

- `tests/unit/event/__init__.py`
- `tests/unit/event/test_event_engine.py`

Future tests must cover valid/invalid envelope, registration, one/multiple
sequential handlers, registration order, snapshot isolation, no-handler,
handler failure and stop, count semantics, no retry, unchanged envelope/event,
no persistence/broker, and absence of historical Event/API. Publisher and
Registry integration tests remain deferred to Stage 6.3.2.
