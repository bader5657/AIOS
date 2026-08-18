# State, Async, and Determinism Direction

- `AIOS CORE V1 = STATELESS`.
- `ASYNC AIOS CORE V1` is the required direction; no second synchronous v1 API.
- The same valid bounded input under the same active authority must yield a
  deterministic routing disposition.

There is no persistent/session state, cache, history, database, event log,
hidden mutable global decision state, random behavior, probabilistic decision,
LLM decision, or hidden heuristic routing. Exact async API remains deferred.
