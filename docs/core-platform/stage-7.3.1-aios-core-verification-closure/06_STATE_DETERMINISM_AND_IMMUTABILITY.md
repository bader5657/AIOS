# State, Determinism, and Immutability

`AIOSCore` has empty slots and no mutable routing state, history, session,
cache, or decision counter. Repeated calls are independent. The same valid
envelope returns an equal result, and different valid envelopes route to the
same sole target.

There is no randomness, time-based routing, or external call. Route neither
assigns to nor reconstructs the `EventEnvelope` or its contained `DomainEvent`;
both retain their original identities and values after routing.
