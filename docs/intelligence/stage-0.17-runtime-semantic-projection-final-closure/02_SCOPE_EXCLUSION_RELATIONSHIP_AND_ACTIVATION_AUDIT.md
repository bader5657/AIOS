# Scope, Exclusion, Relationship, and Activation Audit

The exact implementation paths are:

1. `core/ingestion/semantic_projection.py`;
2. `tests/unit/core_platform/test_semantic_projection.py`.

The production module has zero imports. It has no Telegram, RequestContext,
InputType, EventEnvelope, Mapper, BrainInput, Receiver, Invoker, provider,
Ollama, Registry/database, filesystem/network, environment/configuration,
logging, persistence, Memory, Specialist, or business/domain dependency.

Projection data contains no provenance or correlation field. The function does
not inspect business meaning or implement secret/DLP detection. It performs no
I/O or side effect and creates no runtime identity.

Its output is compatible with a future CoreToBrainMapper `data` argument, but
the projector does not call Mapper, Receiver, Invoker, or Brain. Universal
Ingestion, RequestContext, EventEnvelope, Mapper, Brain components, Stage 8
policy, production startup, deployment, and dependencies remain unchanged.

Repository capability is not activation. No real runtime source is wired into
the projector; no production continuation, inference, composition, schema
binding, or Level B authority exists.
