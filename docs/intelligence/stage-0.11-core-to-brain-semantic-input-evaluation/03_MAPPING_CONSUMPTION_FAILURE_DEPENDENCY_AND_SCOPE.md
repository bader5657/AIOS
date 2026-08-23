# Mapping, Consumption, Failure, Dependency, and Scope

## Mapping owner

A future explicit Core-to-Brain boundary mapper owns:

`Core readiness + separately authorized semantic source → BrainInput`

It must require successful `AIOS_BRAIN_BOUNDARY` readiness but must not infer
semantic input from `CoreRouteResult`. The mapper is a boundary integration
component, not behavior added to `AIOSCore.route`. Its exact implementation
module is deferred to implementation approval; it may depend on public Core
contracts and the Brain-facing `BrainInput` contract only.

## Brain consumption

A future small Brain receiver accepts one `BrainInput`, resolves the approved
Brain-owned intent policy into `instruction`, `timeout_ms`, and
`output_schema_ref`, applies the identifier equality gate, and calls the
existing `BrainInferenceInvoker` with explicit arguments. Stage 0.9's invoker
signature remains unchanged. This is the smallest later change and keeps
mapping/policy outside the provider seam.

## Failure semantics

Construction, readiness, semantic-source, identifier, intent-policy, or
equality failures are boundary/contract failures before inference. They must
not be represented as a provider `FailureCode`, must not claim downstream
success, and must cause zero provider requests. A later implementation approval
must define a bounded boundary failure result/taxonomy; no exception text may
contain content.

## Dependency direction

The legal future direction is:

`boundary mapper → public Core readiness contracts + BrainInput contract`

and:

`Brain receiver → BrainInput + BrainInferenceInvoker`

`AIOSCore` does not import Brain. Brain contracts and receiver do not import
`AIOSCore`, `CoreRouteResult`, or `EventEnvelope`. Provider modules do not
import Core or the boundary mapper. Production composition remains separately
unresolved.

## Privacy and excluded state

No instruction/data content logging is allowed. Bounded logs may contain only
`correlation_id`, `request_id`, and boundary status. Persistence, session,
Memory, Specialist routing, business fields/actions, retry, fallback, tools,
and production activation are all `NONE`.
