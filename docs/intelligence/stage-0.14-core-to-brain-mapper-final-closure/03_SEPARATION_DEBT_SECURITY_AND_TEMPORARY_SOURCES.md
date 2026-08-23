# Separation, Deferred Debt, Security, and Temporary Sources

## Permanent mapper/receiver separation

CoreToBrainMapper owns Core eligibility, correlation-ID preservation, Brain
request-ID generation, static BrainIntent assignment, semantic data mapping,
opaque provenance mapping, and BrainInput construction.

BrainSemanticReceiver exclusively owns instruction, timeout, output-schema
reference, and inference invocation. No responsibility overlaps.

## Preserved debt and boundaries

Actual runtime/service wiring

`AIOS_BRAIN_BOUNDARY → CoreToBrainMapper → BrainSemanticReceiver`

is not implemented or authorized. Mapper-to-receiver operation has not yet been
verified as one repository chain and requires separate controlled integration
authority before any production wiring.

Production schema resolver/validator binding and the production composition
root remain unresolved. Stage 0.14 performs no integration, live inference,
production activation, runtime/VPS mutation, Memory, Specialist routing,
business action, persistence, or logging.

Stage 0.8, Stage 0.10, and Stage 0.13 temporary staging sources remain
preserved. Cleanup remains separately governed.
