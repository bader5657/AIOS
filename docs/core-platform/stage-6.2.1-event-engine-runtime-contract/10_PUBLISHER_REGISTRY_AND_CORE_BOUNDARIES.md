# Publisher, Registry, and AIOS Core Boundaries

Conceptual flow remains:

`Integration/Application publisher`
→ `EventEnvelope construction`
→ `EventEngine.process(envelope)`
→ `EventDeliveryResult`
→ `AIOS Core boundary`

The publisher constructs the envelope and remains outside Event Engine. Event
Engine creates neither DomainEvent nor EventEnvelope.

Stage 6.2.1 does not wire PostgreSQL Registry to Event Engine. Registry ends at
its bounded persistence disposition; Event Engine does not infer events from
Registry rows or import persistence semantics. Execution Plan Stage 6.3.2 owns
that later integration under separate approval.

Handlers conceptually deliver toward the AIOS Core boundary. This contract
does not create concrete Core consumers, Brain, Memory, Specialist Router,
Specialists, placeholder modules, or business handlers. Future unit tests use
test-local handlers only.
