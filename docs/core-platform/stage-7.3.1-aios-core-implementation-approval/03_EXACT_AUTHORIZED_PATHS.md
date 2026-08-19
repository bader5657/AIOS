# Exact Authorized Paths

Only these four paths may change during the later Stage 7.3.1 implementation.

## Runtime

- `core/aios_core/__init__.py`
- `core/aios_core/core.py`

## Unit tests

- `tests/unit/aios_core/__init__.py`
- `tests/unit/aios_core/test_aios_core.py`

Repository convention uses lower-case underscore package names beneath `core/`
and mirrored unit-test packages. No current path conflicts with `aios_core`.
No integration test is authorized.

If a fifth path or another runtime package is required, stop with:

`STAGE 7.3.1 SCOPE EXPANSION REQUIRED`
