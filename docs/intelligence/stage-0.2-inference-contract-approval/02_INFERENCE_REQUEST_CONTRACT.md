# InferenceRequest Contract

## Identity and purpose

`InferenceRequest` is a Brain-owned, runtime-local, non-canonical,
provider-neutral representation of exactly one bounded inference invocation.
It is stateless and is not a persistence or business/domain entity.

It must be a frozen, slotted dataclass. Construction must take an immutable
snapshot of nested payload/reference structures so caller mutation cannot
alter the constructed request.

## Field disposition

| Field | Disposition | Approved semantics |
|---|---|---|
| `schema_version` | REQUIRED | positive integer; initial and sole accepted v1 value `1`; unsupported value fails closed |
| `correlation_id` | REQUIRED | non-empty bounded opaque string; no user/business meaning; preserved exactly into result |
| `request_id` | REQUIRED | non-empty bounded opaque string identifying one invocation; preserved exactly into result; no persistence meaning |
| `capability` | REQUIRED | `InferenceCapability` enum; v1 accepts only `STRUCTURED_INFERENCE` |
| `input_payload` | REQUIRED | bounded recursively immutable JSON-compatible mapping; transient; no binary/provider object/full canonical object by default |
| `timeout_ms` | REQUIRED | positive integer; Brain-owned ceiling; provider may shorten but never extend |
| `output_schema_ref` | REQUIRED | non-empty bounded provider-neutral identifier referencing an approved bounded output schema |
| `input_reference` | OPTIONAL | nullable bounded opaque provenance string; never automatically dereferenced or fetched |
| `context_references` | OPTIONAL | immutable bounded tuple of opaque references; no retrieval or Memory semantics |
| `deadline` | DEFERRED | absent from v1 to avoid dual timeout authority |
| `provider_configuration_ref` | PROHIBITED | provider/model selection remains configured outside each request |
| `model_configuration_ref` | PROHIBITED | provider/model selection remains configured outside each request |
| tools/functions | PROHIBITED | no tool contract or authority |
| session/persistence/Memory | PROHIBITED | stateless per invocation |
| Specialist/business actions | PROHIBITED | no routing or workflow semantics |

Exact maximum identifier length, reference count, payload depth/size, timeout
range, and approved output-schema identifier allowlist must be named by the
future implementation approval. Their absence does not authorize unbounded
values.

## Capability enum

The complete initial enum is:

```python
class InferenceCapability(str, Enum):
    STRUCTURED_INFERENCE = "structured_inference"
```

No chat, reasoning, completion, tool, Specialist, Memory, or business
capability value exists. Adding a value requires separate evidence and
authority.

## Canonical and content boundary

Brain applies approved data/policy controls before construction. Bounded raw
text may be carried only inside `input_payload`. `EventEnvelope`,
`RequestContext`, Manifest, Registry rows, transport objects, domain entities,
and business records are not embedded wholesale. Optional references remain
opaque provenance and transfer no Registry, Storage, network, or retrieval
ownership to inference.

`output_schema_ref` identifies an approved static schema; it is not executable
content, an arbitrary provider-native schema, or authority to load one from a
network location.
