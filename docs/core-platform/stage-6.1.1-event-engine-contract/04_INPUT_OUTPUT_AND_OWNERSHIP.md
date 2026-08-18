# Input, Output, and Ownership

| Boundary | Approved Stage 6.1.1 contract |
|---|---|
| Publisher | Bounded Integration/Application-layer producer outside Registry and Event Engine |
| Concrete publisher implementation | **DEFERRED** |
| Envelope construction | Publisher/integration boundary |
| Process input | One already-constructed `EventEnvelope` as the primary and smallest contract |
| Optional upstream value | Only an opaque bounded registration reference if later authority proves it necessary |
| Process output | Runtime-neutral bounded success or failure disposition toward AIOS Core |
| Downstream consumer | AIOS Core boundary position only; no concrete consumer |

The publisher receives already-approved upstream registration disposition and
already-authorized Domain Event exposure. It wraps but does not change one
DomainEvent. The Event Engine must not reconstruct the event, infer domain
semantics from Registry rows, mutate payload, generate domain facts, or create
the envelope.

The input excludes a full Registry row as semantic input, PostgreSQL
connections, Storage objects, Manifest artifacts, and wholesale Request
Context. The output is not a subscriber receipt, acknowledgement, handler
result, retry result, broker offset, or queue state.
