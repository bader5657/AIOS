# Dependency, Composition, Activation, and Scope

## Receiver and dependency direction

Future wiring must receive an already-prepared async Brain boundary dependency;
it must not construct `OllamaInferenceProvider`, discover a receiver through the
environment, or own provider/model/network lifecycle. The mapper must be an
explicit lifecycle dependency, constructed once by the future assembly layer
or injected with the receiver. It remains the sole request-ID owner.

Directly importing `BrainSemanticReceiver` from general Stage 8 Core ingestion
would broaden the currently narrow Core-to-Brain dependency policy. A neutral
async callable/protocol may preserve direction, but no such port currently
exists and this evaluation does not invent or approve it. The Project Owner
must choose between an exact narrow boundary import expansion and one minimal
Core-side async port after the semantic ingress contract is fixed.

## Schema and composition prerequisites

Production schema resolver/validator binding for
`brain_structured_inference_result_v1` is not required for an inactive,
repository-only wiring implementation tested with fakes. It is a hard
prerequisite to staging or production-capable receiver activation.

Production composition is likewise not required to unit-test a bounded wiring
component with injected fakes. A stable runtime assembly location is required
before any staging or production activation. The current entrypoint directly
constructs only the Telegram `Application`; no application composition root
assembles Event Engine, AIOSCore, mapper, receiver, invoker, schema binding, or
provider.

## Activation levels

1. **Level A — inactive repository wiring:** eligible only after semantic
   ingress, result destination, dependency seam, and exact paths are approved;
   fake dependencies only, no production receiver supplied.
2. **Level B — controlled staging:** separate later authority after schema
   binding and isolated composition exist; synthetic data only.
3. **Level C — production:** not authorized.

No service-unit change is indicated for Level A. A future application assembly
module may be required before Level B, but its exact path cannot be selected
until composition ownership is approved. `AIOSCore`, Mapper, Brain contracts,
Receiver, Invoker, Telegram adapter, provider adapters, Domain, Registry, and
Event Engine are not approved implementation paths under the current decision.

Persistence, Memory, Specialist routing, business behavior, retry, fallback,
Ollama lifecycle, model pulls, network/firewall changes, database management,
and Telegram polling management remain `NONE`.
