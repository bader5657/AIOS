# Result, Failure, Containment, State, and Boundary Evidence

## Parsing, validation, and success

The adapter bounds the provider envelope, requires the configured model,
completion state, and string `message.content`, parses exactly one JSON mapping,
rejects non-finite constants, independently validates schema conformance, and
then constructs the approved `InferenceResult` only.

Success preserves schema/correlation/request identity, includes validated
structured output plus exact provider/model metadata and bounded monotonic
duration, and contains no provider-native response.

## Failure and cancellation

Only the existing `FailureCode` values are used: request/payload/schema-ref
failure is `INVALID_REQUEST`; narrow connection failure is
`RUNTIME_UNAVAILABLE`; deadline expiry is `TIMEOUT`; generic HTTP/provider or
incomplete/mismatched provider execution is `PROVIDER_FAILURE`; malformed,
non-object, non-finite, contract-invalid, or schema-invalid output is
`MALFORMED_OUTPUT`.

No policy or resource heuristic was invented. `POLICY_DENIED` and
`RESOURCE_LIMIT` remain reserved for positively authorized/identified future
signals. `asyncio.CancelledError` propagates unchanged. Failure details are
bounded sanitized constants; structured output is absent on failure.

The accepted Stage 0.6.4 invalid confidence value remains fail-closed: the
adapter does not coerce `100` to `1.0`, repair output, retry, or hide invalid
content.

## Containment, state, and lifecycle

Raw provider response/error/content is transient only and never returned,
persisted, cached, or logged. No logging was added. There is no request/result
history, conversation, session, embedding, Memory, retry, fallback, routing,
or persistence.

The adapter does not start/stop Ollama, pull/preload a model, perform health
checks, manage containers/network/firewall/filesystem, or change resource
ceilings.

Core remains unchanged at `AIOS_BRAIN_BOUNDARY`, with no reverse dependency.
The adapter uses relative Brain imports and is not registered or wired into
Brain orchestration, Core, services, production, or business flows.
