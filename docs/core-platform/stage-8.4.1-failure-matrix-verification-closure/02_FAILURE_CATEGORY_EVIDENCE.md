# Mandatory Failure-Category Evidence

All mandatory categories passed:

1. Storage failure suppressed Metadata, Manifest, Registry, Event, Core, and
   acknowledgement.
2. Metadata failure propagated after Store Original and preserved the original.
3. Manifest failure propagated, preserved original and metadata, and left no
   valid completed Manifest.
4. Registry persistence failure rolled back its local transaction and committed
   no failed row.
5. Unexpected Registry exception propagated without Event, Core, or
   acknowledgement.
6. `INVALID_ENVELOPE` produced Core-zero gating through a legitimate injected
   bounded result; unchanged Stage 6 tests remain the primary semantic proof.
7. `NO_HANDLER` preserved the committed Registry row and suppressed Core.
8. `HANDLER_FAILURE` preserved the committed row and earlier successful handler
   effect without compensation.
9. Unexpected Event Engine exception propagated after Registry commit and
   suppressed Core and acknowledgement.
10. Bounded Core failure followed successful Event processing, called Core once,
    returned no route readiness, and preserved completed upstream state.
11. Unexpected Core exception propagated after successful Event processing and
    emitted no acknowledgement.

Brain invocation was zero for every category. No new failure code or runtime
mapping was introduced.
