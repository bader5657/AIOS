# Receiver, Policy, Propagation, and Identity Evidence

`BrainSemanticReceiver` exists in `core/brain/receiver.py`, has exactly one
validated `BrainInferenceInvoker` constructor dependency, and exposes one
async `receive(brain_input: BrainInput) -> InferenceResult` path.

Its private policy consists of a frozen/slotted `_IntentPolicy` and immutable
`MappingProxyType` mapping with exactly one entry:

| Policy | Exact value |
|---|---|
| Intent | `BrainIntent.STRUCTURED_INFERENCE` |
| Instruction | `Analyze the provided data and return one concise result string in the required structured output.` |
| Timeout | `120000` ms |
| Output schema reference | `brain_structured_inference_result_v1` |

There is no caller override, default policy, dynamic registry, provider/model
selection, schema resolution, or schema validation.

## Direct propagation and ID control

Correlation ID, request ID, data, input reference, and context references are
passed directly from the immutable `BrainInput`. The method accepts no
duplicate ID or policy arguments and performs no regeneration, enrichment,
mutation, dereference, or provider-native conversion.

Therefore `ID_MISMATCH_STRUCTURALLY_PREVENTED`. This permanently carries
forward the Stage 0.10 rule: downstream side-effecting paths derive IDs from
immutable controlling input and fail before inference rather than reconcile
duplicate manually entered values.

The receiver performs exactly one invoker call and returns its exact
`InferenceResult` object unchanged. There is no wrapper, normalization,
failure-code rewrite, success reinterpretation, retry, fallback, health call,
loop, or second request.
