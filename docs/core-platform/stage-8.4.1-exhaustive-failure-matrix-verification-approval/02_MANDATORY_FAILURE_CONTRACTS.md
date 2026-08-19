# Mandatory Failure Contracts

The dedicated matrix must cover exactly these mandatory categories:

1. Storage failure
2. Metadata failure
3. Manifest failure
4. Registry persistence failure
5. Event Engine `INVALID_ENVELOPE`
6. Event Engine `NO_HANDLER`
7. Event Engine `HANDLER_FAILURE`
8. unexpected Event Engine exception
9. AIOS Core bounded failure
10. unexpected AIOS Core exception

An unexpected Registry exception is additionally required as propagation
evidence. It must remain unmapped and suppress Event and Core execution.

## Component contracts

- Storage failure suppresses Metadata, Manifest, Registry, Event, Core, and a
  success acknowledgement. Telegram temporary download cleanup follows the
  current contract. Partial destination cleanup beyond that contract is not
  guaranteed.
- Metadata failure propagates after a possible successful store. It preserves
  the stored original and suppresses all later stages.
- Manifest failure propagates after Storage and Metadata. It preserves those
  completed artifacts, leaves no valid completed Manifest, and suppresses
  Registry, Event, and Core.
- Registry persistence failure rolls back its local failed transaction, leaves
  no committed failed row, preserves upstream artifacts, and suppresses Event
  and Core.
- Event bounded failures preserve the committed Registry row and upstream
  artifacts and suppress Core.
- Unexpected Event exceptions propagate after Registry commit and suppress
  Core.
- Core bounded failure returns no route readiness and preserves all completed
  upstream state.
- Unexpected Core exceptions propagate after successful Event processing and
  preserve all completed upstream state.

No case authorizes a new failure code or exception mapping.
