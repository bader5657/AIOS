# State, Determinism, and Immutability

The same valid EventEnvelope under the same code and authority must always
produce the same result. Different valid envelopes also route to the same sole
target.

No randomness, time-dependent routing, route history, session or conversation
state, decision counter, mutable cache, database, or mutable global decision
state is permitted. An `AIOSCore` instance requires no mutable routing state.

Route must leave both the EventEnvelope and contained DomainEvent unchanged.
No semantically modified copy or envelope reconstruction is needed.
