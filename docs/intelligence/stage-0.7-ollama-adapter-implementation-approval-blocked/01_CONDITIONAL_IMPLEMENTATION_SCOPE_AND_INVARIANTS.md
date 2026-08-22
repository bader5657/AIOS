# Conditional Implementation Scope and Invariants

The following findings are technically sufficient only after a separate input
payload contract approval. They are recorded to avoid reopening settled Stage
0.7 decisions, but are not implementation authority.

## Proposed repository paths

Repository convention uses `__init__.py` for Brain and concrete adapter
packages. The complete proposed path set remains exactly three paths:

1. `core/brain/providers/__init__.py`;
2. `core/brain/providers/ollama.py`;
3. `tests/unit/brain/providers/test_ollama.py`.

The schema seam can be expressed as small injected callables/protocols in
`ollama.py`; no fourth implementation module or full schema registry is needed.
Authorized implementation path count under this blocked record is `0`.

## Configuration and descriptor

The conditional `OllamaProviderConfig` is a frozen, slotted dataclass with
exactly `base_url`, `model_id`, `timeout_ceiling_ms`, and `keep_alive`.

- the initial endpoint configuration is exactly the approved local/private
  `http://172.31.63.2:11434`, but the adapter logic must not hard-code it;
- URL validation rejects malformed/non-HTTP/public URLs, credentials, query,
  and fragment; HTTPS is not assumed for this isolated local endpoint;
- model ID is exactly `qwen2.5:1.5b-instruct-q4_K_M`, with no dynamic or
  per-request override;
- timeout ceiling is exactly `120000 ms`, effective as
  `min(request.timeout_ms, timeout_ceiling_ms)`;
- `keep_alive` is exactly `5m`, with no request override; and
- credentials, retry, fallback, Telegram, database, business, and production
  configuration are absent.

The descriptor remains exactly `ollama-local`, the configured Qwen model,
`ProviderRuntimeKind.LOCAL`, and sole `STRUCTURED_INFERENCE` capability.

## Transport and schema seam

Use the already pinned `httpx==0.28.1` through an injected
`httpx.AsyncClient`. Execution is one asynchronous `POST /api/chat`, no health
preflight, no retry, no provider SDK, and no new dependency.

The smallest conditional schema seam is two injected callables:

- resolver: approved opaque `output_schema_ref` to an immutable bounded local
  JSON Schema mapping; and
- validator: `(schema_ref, parsed_mapping)` to a conformance result or bounded
  validation exception.

The adapter sends the resolved schema through Ollama `format`, then invokes the
independent validator after parsing. Unknown refs fail `INVALID_REQUEST`.
Provider-side schema compliance is defense in depth only. The seam creates no
registry, persistence, remote resolution, or fourth source path.

## Deterministic settings

Benchmark-only temperature, seed, `num_ctx`, and `num_predict` values are not
automatically approved as permanent adapter behavior. They must not be accepted
as arbitrary provider-native request payload fields. Their future ownership
requires the input-payload/prompt-policy decision or a separately approved
static staging policy. Until then the implementation has no authority to bake
them into adapter logic.

## Conditional request/response behavior

Once an exact payload envelope is approved, translation must verify the sole
capability, static configured model, approved schema reference, and exact
payload shape; construct one non-streaming request with configured model and
`keep_alive`; and invent no task intent or business meaning.

Required response evidence is limited to HTTP status, `model`, `done`, and
`message.content`. Duration is measured with a monotonic clock. Provider timing
metadata is optional and need not cross the boundary. Raw content remains
transient and is discarded.

The parsing sequence remains:

1. check request/capability;
2. resolve output schema;
3. construct the provider request;
4. perform one async HTTP request;
5. verify the HTTP response;
6. parse the provider envelope;
7. extract `message.content`;
8. parse exactly one JSON object;
9. independently validate schema conformance;
10. construct `InferenceResult`; and
11. discard provider-native/raw content.
