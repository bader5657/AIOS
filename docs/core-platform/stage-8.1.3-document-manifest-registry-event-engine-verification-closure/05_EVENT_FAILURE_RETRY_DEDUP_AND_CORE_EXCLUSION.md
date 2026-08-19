# Event Failure, Retry, Deduplication, and AIOS Core Exclusion

The real Event Engine with no matching handler returned `NO_HANDLER` after one
process call. A test-local async handler that raised returned
`HANDLER_FAILURE` after one handler execution. Both paths preserved the
committed Registry row and upstream artifacts and performed no compensation or
retry.

An injected unexpected `EventEngine.process()` exception propagated under the
existing contract after Registry commit. Independent database inspection found
the row still committed; the original and Manifest remained intact; no error
mapping, compensation, or automatic retry was introduced.

Static and behavioral evidence proved no retry, backoff, retry counter,
idempotency key, processed-event ledger, dedupe cache, or duplicate suppression.
Two explicit repeated ingestions created two independent Registry rows and two
independent handler executions, preserving the absence of deduplication
semantics.

The focused source contained no AIOS Core import, construction, or route call.
Static endpoint audit confirmed `AIOSCore.route()` call count was zero. Stage
8.1.3 ended before AIOS Core, leaving that integration to Stage 8.1.4.
