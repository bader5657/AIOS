# Fixed Input, Mapper, BrainInput, and Receiver Policy

## Exact entry and caller values

Use `CoreRouteResult` with exactly `success=True`,
`route_target=CoreRouteTarget.AIOS_BRAIN_BOUNDARY`, `failure_code=None`, and
`failure_reason=None`. Do not invoke AIOSCore or construct EventEnvelope or
RequestContext.

Freeze:

- correlation ID: `stage-0.15-correlation-1`;
- UUIDv4: `01234567-89ab-4def-8123-456789abcdef`;
- expected request ID: `brain-0123456789ab4def8123456789abcdef`;
- data: `{"temperature_c": 25.0, "vibration": 0.12, "status": "stable"}`;
- input reference: `stage-0.15-synthetic-input-1`; and
- context references: `("stage-0.15-context-1", "stage-0.15-context-2")`.

The deterministic local factory must prove the UUID is version 4, count calls,
and return this exact UUID. The integration caller invokes `mapper.map(...)`
once and asserts exact BrainInput type, schema version, IDs,
STRUCTURED_INFERENCE intent, semantic data, and provenance.

Use mutable source data, mutate it after mapping, and prove BrainInput and the
later InferenceRequest retain the original immutable snapshot. CoreRouteResult
and routing fields must not be embedded.

## Receiver policy

Call exactly `await receiver.receive(brain_input)`; the integration caller must
not directly call the invoker or provider. The captured request must prove the
receiver selected exactly:

- instruction: `Analyze the provided data and return one concise result string in the required structured output.`;
- timeout: `120000` ms; and
- schema reference: `brain_structured_inference_result_v1`.

There is no caller override or duplicate downstream identifier.
