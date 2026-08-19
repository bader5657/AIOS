# Respond, Failure, and Transaction Evidence

## Respond authority

`Respond = Telegram transport receipt/readiness acknowledgement only`

The gate remains `register_handoff_ready == True`. Acknowledgement is not Registry, Event, Core, Brain, business, or end-to-end semantic success. In particular:

- `acknowledgement != Registry success`
- `acknowledgement != Event success`
- `acknowledgement != Core success`
- `acknowledgement != Brain success`
- `register_handoff_ready != route_handoff_ready`
- `route_handoff_ready != Brain execution`

After bounded Registry/Event/Core failure, acknowledgement may occur when `register_handoff_ready` remains true. This is accepted receipt/readiness behavior. `RESPOND EXIT-GATE ISSUE = NONE`.

## Mandatory failure matrix

The complete matrix covers Storage, Metadata, Manifest, Registry persistence, unexpected Registry exception, INVALID_ENVELOPE, NO_HANDLER, HANDLER_FAILURE, unexpected Event exception, bounded Core failure, and unexpected Core exception.

Suppression is verified: Storage failure suppresses Metadata/Manifest/Registry/Event/Core; Metadata failure suppresses Manifest/Registry/Event/Core; Manifest failure suppresses Registry/Event/Core; Registry failure suppresses Event/Core; Event failure suppresses Core; Core failure invokes no Brain.

Preservation is verified: Metadata failure preserves original; Manifest failure preserves original and metadata; Registry failure preserves original, metadata, and Manifest while committing no failed row; Event failure preserves committed Registry and all upstream artifacts; Core failure also preserves the completed Event result.

## Execution model

- `TRANSACTION MODEL = COMPONENT-LOCAL ONLY`
- `RETRY = NONE`
- `COMPENSATION = NONE`
- `DEDUPLICATION / IDEMPOTENCY = NONE`

No component-spanning transaction, distributed rollback, hidden backoff, reroute, processed-event cache, event ledger, or route ledger exists.
