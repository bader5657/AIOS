# Event Success Gate and Call Counts

AIOS Core eligibility is exactly `EventDeliveryResult.success is True` after
`await EventEngine.process(envelope)` completes.

| Upstream disposition | Event Engine calls | AIOS Core calls |
|---|---:|---:|
| no DomainEvent | 0 | 0 |
| `INVALID_ENVELOPE` | 1 | 0 |
| `NO_HANDLER` | 1 | 0 |
| `HANDLER_FAILURE` | 1 | 0 |
| Event Engine success | 1 | exactly 1 |

No failure code is translated into a Core failure code. There is no fallback
Core invocation. Registration without a DomainEvent remains successful and is
not a Core failure.

An unexpected Event Engine exception retains the existing propagation
contract, makes zero Core calls, and makes no downstream-readiness claim.
