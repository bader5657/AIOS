# Receiver API, Static Policy, and Schema Decisions

## Proposed API and dependency

The minimal class is `BrainSemanticReceiver` in `core/brain/receiver.py`.
Its constructor accepts exactly one `BrainInferenceInvoker`. Its async method:

```python
async def receive(self, brain_input: BrainInput):
    ...
```

The return value is the invoker's exact `InferenceResult`; v1 adds no direct result-contract import merely for annotation. Wrong invoker or input types raise `TypeError`. No protocol, generalized policy
engine, registry, separate production policy module, or third implementation
path is required.

## Policy representation

V1 policy is one private frozen/slotted record and one private immutable
`MappingProxyType` mapping inside `receiver.py`, keyed by `BrainIntent`. It is
not constructor-injected because the sole vocabulary is frozen. It contains
exactly instruction, timeout, and output-schema reference—no provider/model,
endpoint, retry, fallback, Memory, Specialist, tool, or business setting.

## Exact v1 policy

| Value | Decision |
|---|---|
| Intent | `BrainIntent.STRUCTURED_INFERENCE` |
| Instruction | `Analyze the provided data and return one concise result string in the required structured output.` |
| Timeout | `120000` ms |
| Output schema reference | `brain_structured_inference_result_v1` |

The instruction is static and provider-neutral. It is never built from data,
references, transport text, or arbitrary caller content.

## Approved referenced schema

`brain_structured_inference_result_v1` identifies this exact bounded static
schema semantically:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["result"],
  "properties": {
    "result": {"type": "string", "minLength": 1, "maxLength": 4096}
  }
}
```

The receiver selects only the reference. It does not contain, resolve, or
validate the schema. A later composition approval must bind the reference to
this exact schema in the injected resolver/validator before live use.
