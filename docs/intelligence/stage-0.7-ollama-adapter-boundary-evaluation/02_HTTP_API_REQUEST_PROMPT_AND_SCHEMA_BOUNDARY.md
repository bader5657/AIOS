# HTTP API, Request Translation, Prompt, and Schema Boundary

## HTTP and async strategy

`httpx==0.28.1` is already an exact direct project dependency. The minimal
future strategy is an injected `httpx.AsyncClient` (or equivalently injected
bounded async transport using that client), with a single `POST`, streaming
disabled, no retry, and no provider SDK. This preserves the async
`InferenceProvider.infer()` interface without blocking the event loop and adds
no dependency.

The adapter must use an effective timeout no greater than
`min(request.timeout_ms, config.timeout_ceiling_ms)`. It must not use a
standard-library blocking HTTP call directly on the event loop. Thread
offloading is unnecessary while the authoritative async dependency exists.

## Ollama API

The future call is:

- method: `POST`;
- endpoint: `{base_url}/api/chat`;
- content type: `application/json`;
- non-streaming: `stream: false`.

The bounded request body contains only:

- `model`: configured exact model ID;
- `messages`: one user message containing the Brain-owned bounded instruction
  and serialized input data, with no history;
- `format`: the locally resolved approved JSON Schema;
- `stream`: `false`;
- `keep_alive`: configured approved value;
- `options`: approved deterministic/resource-bounded inference options.

No `tools`, images, conversation history, remote URL, credentials, or provider
selection fields are sent. Initial deterministic options should retain the
validated benchmark profile where applicable: temperature `0`, seed `42`,
context `512`, and maximum predicted tokens `32`. Changing those values needs
explicit implementation/integration-test authority.

The only provider response fields needed are `model`, `message.content`, and
`done`. HTTP status and response-envelope validity are also checked. Duration
is measured locally with a monotonic clock; provider timing/token fields do not
cross the boundary. `done` must be true, `model` must match the configured
model, and `message.content` must be a string. All other fields are ignored and
discarded.

Ollama's official API documents `format` as either JSON mode or a JSON Schema,
and documents `message.content` as the chat output. The provider-side `format`
constraint is defense in depth only; it is not AIOS schema validation.

Primary API references:

- `https://docs.ollama.com/api/chat`;
- `https://docs.ollama.com/capabilities/structured-outputs`.

## Request translation and prompt ownership

- `capability` must be exactly `STRUCTURED_INFERENCE`; otherwise fail
  `INVALID_REQUEST` before network execution.
- `input_payload` carries the bounded task instruction and bounded JSON data
  constructed by future Brain request-building authority. The implementation
  approval must freeze an exact provider-neutral payload envelope; the adapter
  serializes it without inventing business semantics.
- `timeout_ms` supplies the caller ceiling.
- `output_schema_ref` is resolved only against an injected approved local
  schema authority; it is never sent as a path/URL or dynamically fetched.
- `input_reference` and `context_references` remain opaque provenance and are
  not dereferenced, retrieved, or automatically inserted into the prompt.

Brain/request construction owns task intent, policy-cleared content, and the
actual bounded instruction. The adapter owns only deterministic transport
rendering. It must not embed hidden business prompt policy. The benchmark's
confidence-scale clarification belongs in the task/schema-specific Brain-owned
instruction template, not as an Ollama adapter global prompt.

## Independent output-schema validation seam

Stage 0.4 already reserves provider-neutral schema resolution and conformance
validation. Stage 0.7 therefore requires a small injected
`OutputSchemaResolver`/validator seam owned under `core/brain/`, not inside
Ollama-specific code. For an approved `output_schema_ref`, it must provide the
bounded local schema sent as `format` and independently validate the parsed
output against the same approved schema.

Unknown refs, remote refs, mutable arbitrary schemas, and provider-native-only
validation fail closed. A first static approved-schema mapping is sufficient;
the implementation approval must freeze its interface, path, allowlist, and
validation mechanism. No network schema loading or registry/persistence layer
is authorized.
