# Scope and Correction Contract

Only `tests/unit/core_platform/test_ingestion_capability_matrix.py` may change.

The correction must replace import-order-dependent fake installation with
narrow, explicit per-test patches against the actual imported boundary used by
the subject. Patches must restore automatically after each test and must not
delete broad `core.*` module sets, reload runtime globally, or leak fake modules
into later tests.

All capability cases and assertions remain mandatory. The correction may not
skip, xfail, weaken, remove, or convert assertions into tautologies. Production
imports, dependency behavior, RequestContext, Registry, Telegram, and Stage 8
semantics remain unchanged.

If another path is required, stop with:

`STAGE 8 EXIT GATE SCOPE EXPANSION REQUIRED`
