# Exact Authorized Paths

Only these four paths may change during Stage 6.3.1 implementation.

## Runtime

- `core/event/__init__.py`
- `core/event/event_engine.py`

## Unit tests

- `tests/unit/event/__init__.py`
- `tests/unit/event/test_event_engine.py`

No fifth path is authorized. `event_engine.py` must contain the handler alias,
registration error, failure-code enum, immutable result, and EventEngine. The
package `__init__.py` may expose only the bounded public runtime API.

If another path or dependency becomes necessary, implementation must stop with
`STAGE 6.3.1 SCOPE EXPANSION DECISION REQUIRED` or
`STAGE 6.3.1 DEPENDENCY APPROVAL REQUIRED`, as applicable.
