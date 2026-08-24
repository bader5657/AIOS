# Scope, Tests, and Unchanged Controls

## Exact future implementation scope

The corrected ordering remains implementable within exactly four paths:

1. `core/ingestion/universal_ingestion.py`;
2. `tests/unit/core_platform/test_universal_ingestion.py`;
3. `tests/unit/core_platform/test_stage8_import_boundaries.py`; and
4. `tests/unit/brain/test_inference_contracts.py`.

No fifth implementation path is required. Governance records in this package
do not expand that closed implementation scope.

## Updated mandatory test controls

Future fake-based tests must prove:

1. absent semantic data generates no Stage 0.16 correlation ID;
2. explicit semantic data generates one UUIDv4 correlation before the one
   original EventEnvelope construction;
3. that exact value appears in the EventEnvelope;
4. a non-Brain route may retain it but causes zero Mapper calls, zero Mapper
   request IDs, and zero Brain calls;
5. an eligible Brain route passes the same value to Mapper;
6. Mapper alone owns the distinct Brain request ID;
7. exact BrainInput reaches the boundary once and result identity is preserved;
8. there is no envelope mutation/reconstruction or second route call;
9. there is no retry, fallback, detached task, or blocking bridge; and
10. the inactive production default remains unchanged.

The complete non-live regression matrix from the prior Level A authority
remains mandatory after future implementation.

## Controls unchanged by reconciliation

AIOSCore, EventEnvelope schema and immutability, exact Core routing,
provider-neutral synthetic semantic data, opaque provenance, Mapper injection,
the narrow native-async Brain seam, exact InferenceResult identity, exception
and cancellation propagation, and the three exact import-policy edges remain
unchanged.

No real Telegram/user/business semantic inference, provider dependency,
schema binding, production composition, startup change, logging, persistence,
Memory, Specialist routing, business action, retry, fallback, Level B, or Level
C is authorized.
