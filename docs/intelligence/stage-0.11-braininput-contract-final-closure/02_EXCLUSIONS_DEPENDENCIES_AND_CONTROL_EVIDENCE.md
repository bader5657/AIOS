# Exclusions, Dependencies, and Control Evidence

`BrainInput` contains no instruction, prompt, timeout, output-schema reference,
provider/model/runtime configuration, endpoint, messages, options,
tools/functions, Memory state, Specialist routing, business action,
`EventEnvelope`, or `CoreRouteResult`.

V1 has no `to_dict`, `from_dict`, wire representation, JSON encoder,
persistence representation, logging, or storage behavior. The module uses
standard-library imports only and has no Core, inference/provider
implementation, Ollama, HTTP client, Memory, Specialist, business, or Domain
dependency.

## Stage 0.10 identifier control

Future side-effecting paths must derive `correlation_id` and `request_id`
directly from immutable controlling input wherever possible. They must verify
exact equality and fail before inference on any mismatch. Duplicate manually
entered downstream identifiers are prohibited.

This control is permanent and does not rewrite prior evidence.

## Reviewer finding

One focused source-audit assertion initially matched the approved literal
`structured_inference` as though it were a prohibited implementation import.
The test was narrowed to prohibit actual inference-contract/invoker imports.
No `BrainInput` behavior changed.
