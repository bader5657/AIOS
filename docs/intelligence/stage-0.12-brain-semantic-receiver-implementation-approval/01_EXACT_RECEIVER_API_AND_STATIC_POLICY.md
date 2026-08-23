# Exact Receiver API and Static Policy

## Receiver API

`core/brain/receiver.py` defines:

```python
class BrainSemanticReceiver:
    def __init__(self, invoker: BrainInferenceInvoker) -> None:
        ...

    async def receive(self, brain_input: BrainInput) -> InferenceResult:
        ...
```

The constructor accepts exactly one dependency and validates it with
`isinstance(invoker, BrainInferenceInvoker)`, raising `TypeError` otherwise.
The receiver stores only that invoker. `receive` accepts exactly one
`BrainInput`, validates its type, and exposes no duplicate identifier,
instruction, timeout, schema, provider, or configuration argument.

`InferenceResult` may be imported from the existing Brain inference contract
for the return annotation only. This adds no provider/runtime dependency.

## Private static policy representation

The module defines one private frozen/slotted `_IntentPolicy` dataclass with
exactly:

- `instruction: str`;
- `timeout_ms: int`; and
- `output_schema_ref: str`.

One private `MappingProxyType` mapping binds exactly
`BrainIntent.STRUCTURED_INFERENCE` to:

| Policy field | Exact value |
|---|---|
| `instruction` | `Analyze the provided data and return one concise result string in the required structured output.` |
| `timeout_ms` | `120000` |
| `output_schema_ref` | `brain_structured_inference_result_v1` |

There is no policy injection, environment loading, registry framework, plugin,
caller override, data interpolation, hidden prompt, or speculative intent.
