# Retry Policy and Non-Goals

Automatic retry remains prohibited. Static and behavioral evidence must show
no loop, backoff, retry count, reconnect-and-retry, or conflict retry. One
failed operation produces one Registry-local failure result.

Stage 5.3.2 does not authorize:

- same-row conflict resolution;
- lost-update prevention;
- `SERIALIZABLE`;
- deadlock recovery policy;
- pooling or ORM;
- delete, upsert, merge, or deduplication;
- Registry Entry;
- schema/migration changes;
- runtime API changes; or
- Stage 5.4.1 wiring.
