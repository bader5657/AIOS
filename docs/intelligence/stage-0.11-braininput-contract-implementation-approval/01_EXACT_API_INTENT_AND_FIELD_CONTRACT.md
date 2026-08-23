# Exact API, Intent, and Field Contract

## Local constants and intent

`core/brain/input_contracts.py` defines local constants without importing
inference contracts:

- `BRAIN_INPUT_SCHEMA_VERSION = 1`
- identifier maximum `128`
- reference maximum `512`
- context-reference count maximum `32`
- JSON depth maximum `16`
- direct-container member maximum `256`
- encoded JSON maximum `1_048_576` UTF-8 bytes

It defines exactly this v1 semantic vocabulary:

```python
class BrainIntent(str, Enum):
    STRUCTURED_INFERENCE = "structured_inference"
```

No other intent is authorized. `BrainInput.intent` requires the exact enum
member; an arbitrary/raw string, other enum, provider capability, business
intent, tool, Specialist, or Memory operation is rejected.

## BrainInput API

```python
@dataclass(frozen=True, slots=True)
class BrainInput:
    schema_version: int
    correlation_id: str
    request_id: str
    intent: BrainIntent
    data: Mapping[str, object]
    input_reference: str | None = None
    context_references: tuple[str, ...] = ()
```

These are exactly the seven declared dataclass fields in this order. The class
represents one bounded immutable semantic request presented to the Brain
receiving boundary. It is not `InferenceRequest`, `EventEnvelope`,
`CoreRouteResult`, a provider request, or a business command.

There are no `instruction`, `timeout_ms`, `output_schema_ref`, provider/model,
endpoint, message, prompt, option, tool/function, Memory, Specialist, or
business-action fields.

## Ownership decisions

- originating request context owns `correlation_id`; future mapper copies it;
- future boundary mapper exclusively creates `request_id` once per handoff;
- mapper assigns the approved semantic intent and snapshots authorized data;
- Brain policy later owns instruction, timeout, and output-schema selection;
- Brain receiver must derive invoker IDs directly from `BrainInput`, not accept
  duplicate manually entered identifier arguments.
