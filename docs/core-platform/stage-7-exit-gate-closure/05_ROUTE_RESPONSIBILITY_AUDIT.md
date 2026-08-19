# Route Responsibility Audit

Route is a deterministic bounded decision establishing whether one accepted
`EventEnvelope` is eligible for the sole authorized downstream handoff
category.

It is not network or broker routing, Specialist Router behavior, business-rule
routing, workflow execution, job scheduling, Intelligence, or LLM reasoning.
The only public runtime operation is async `AIOSCore.route`.
