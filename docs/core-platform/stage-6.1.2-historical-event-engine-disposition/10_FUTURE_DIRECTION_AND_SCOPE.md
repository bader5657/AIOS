# Future Implementation Direction

No path is authorized for modification by this package. Likely candidates for
later scope planning, subject to Stage 6.2.1 and a separate implementation
approval, are:

| Category | Likely candidate |
|---|---|
| Runtime package | A fresh `core/event/` boundary with no historical API presumption |
| Process contract | Envelope input validation and bounded disposition types/functions |
| Unit tests | New focused Event Engine tests under `tests/unit/event/` |
| Integration tests | Later Registry/publisher → Event Engine → AIOS Core-boundary tests |

Migration/refactor strategy for later approval:

1. do not restore the historical tree;
2. approve Stage 6.2.1 behavior independently;
3. define a closed runtime/test path list;
4. implement fresh against `EventEnvelope`, importing no old generic Event;
5. add only semantics explicitly approved at that time; and
6. prove no historical API or config claim leaked into authority.

No broker, queue, persistence, publisher implementation, subscriber, or AIOS
Core consumer is included by this direction.
