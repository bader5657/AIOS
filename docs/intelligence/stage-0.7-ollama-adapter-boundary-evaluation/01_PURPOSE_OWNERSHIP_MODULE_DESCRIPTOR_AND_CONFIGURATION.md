# Purpose, Ownership, Module, Descriptor, and Configuration

## Exact adapter purpose

The complete responsibility is:

`InferenceRequest → translate → one local Ollama request → transient parse → independent schema validation → InferenceResult`

The adapter does not create task intent, reinterpret business/domain data,
orchestrate Brain work, select a provider/model dynamically, execute tools,
route to Specialists, access Memory, persist data, or complete a business
workflow.

## Ownership and module

The adapter is an AIOS Brain provider-adapter implementation. It is not owned
by Core Platform and does not create a new Intelligence architecture layer.
The exact future class and repository path are:

- class: `OllamaInferenceProvider`;
- module: `core/brain/providers/ollama.py`;
- package marker if required: `core/brain/providers/__init__.py`.

Introducing `providers/` is an organizational Brain subpackage for concrete
implementations behind `core.brain.provider`; it changes no ownership,
dependency direction, public contract, or canonical architecture.

## Exact descriptor

The future immutable descriptor is:

| Field | Value |
|---|---|
| `provider_id` | `ollama-local` |
| `model_id` | `qwen2.5:1.5b-instruct-q4_K_M` |
| `runtime_kind` | `ProviderRuntimeKind.LOCAL` |
| `capabilities` | `(InferenceCapability.STRUCTURED_INFERENCE,)` |

Provider and model identity are static constructor-time configuration. No
per-request override, discovery, routing, or fallback exists.

## Runtime endpoint and configuration ownership

The verified current staging endpoint is
`http://172.31.63.2:11434`, reachable only from an approved peer attached to
the private isolated runtime network. The IP is evidence, not a permanent code
constant.

The smallest future representation is a frozen, slotted
`OllamaProviderConfig` colocated in `core/brain/providers/ollama.py`, containing
exactly:

- `base_url`;
- `model_id`;
- `timeout_ceiling_ms`, initially `120000`;
- `keep_alive`, initially `5m`.

The provider identifier remains the stable adapter identity `ollama-local`.
Configuration is constructor-injected and immutable. A future staging
composition root may read environment-backed deployment settings and build the
config, but the adapter itself must not read environment variables implicitly.
Configuration does not enter `InferenceRequest`, canonical objects, or Core.
Local Ollama requires no credentials.

Endpoint validation must reject non-HTTP schemes, embedded credentials, query
or fragment components, and endpoints outside the separately approved
local/private topology. Production configuration remains absent.
