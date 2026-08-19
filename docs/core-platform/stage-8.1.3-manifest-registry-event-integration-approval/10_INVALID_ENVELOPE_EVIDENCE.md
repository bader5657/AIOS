# INVALID_ENVELOPE Evidence Disposition

The conforming end-to-end path constructs a valid EventEnvelope. The focused test
must not corrupt DomainEvent or runtime state merely to manufacture an invalid
envelope.

Stage 8.1.3 accepts unchanged Stage 6 unit and regression evidence as the primary
source for Event Engine `INVALID_ENVELOPE` production. The focused Stage 8 test may
add legitimate injected `EventDeliveryResult` projection evidence if it can do so
without replacing or changing orchestration behavior.

Either accepted source must prove that Universal Ingestion preserves
`INVALID_ENVELOPE` exactly as attempted `True`, succeeded `False`, with the same
failure code. No malformed production object or new failure path is authorized.
