# State, Async, and Determinism

AIOS Core v1 is stateless and async-only. Each direct awaited Route call depends
only on the supplied EventEnvelope and active contract.

The same accepted envelope under the same authority produces the same result.
No route history, session/conversation state, cache, database, global mutable
decision state, randomness, heuristic variation, LLM, background task, task
spawning, or parallel fan-out is permitted.
