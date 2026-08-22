# Implementation, Configuration, Descriptor, Payload, and HTTP Evidence

## Closed-world implementation evidence

PR `#138` and merge `c64ae6d9364e175351aa7139f8da052d38056598`
changed exactly:

1. `core/brain/providers/__init__.py`;
2. `core/brain/providers/ollama.py`;
3. `tests/unit/brain/providers/test_ollama.py`;
4. `tests/unit/core_platform/test_stage8_import_boundaries.py`.

No unauthorized fifth path exists in the implementation diff.

## Configuration and descriptor

`OllamaProviderConfig` is a frozen, slotted dataclass with exactly `base_url`,
`model_id`, `timeout_ceiling_ms`, and `keep_alive`. URL validation accepts only
bounded private/loopback HTTP endpoints with explicit host/port and no
credentials, query, fragment, or public/unspecified/multicast target.

The model is statically bound to `qwen2.5:1.5b-instruct-q4_K_M`; timeout ceiling
is `120000 ms`; keep-alive is `5m`; no request override or dynamic model choice
exists. The immutable descriptor is exactly `ollama-local`, that model,
`LOCAL`, and sole `STRUCTURED_INFERENCE` capability.

## Payload and rendering

Before schema or HTTP side effects, the adapter requires exactly the closed
`instruction`/`data` payload contract: bounded already-trimmed instruction and
mapping data, including `{}`. It rejects missing/unknown/provider-native
top-level fields without coercion.

Rendering is exactly instruction plus `\n\nInput JSON:\n` plus UTF-8-preserving,
non-finite-rejecting, sorted-key compact canonical JSON. The provider body has
exactly one user message, no system/assistant/history/multi-turn/session state,
and no hidden business intent.

## Schema, HTTP, and timeout

The schema resolver and independent validator are constructor-injected. The
opaque `output_schema_ref` remains outside the payload. Ollama `format` is only
provider-side defense in depth; parsed output must separately pass the injected
validator.

An injected pinned `httpx.AsyncClient` executes exactly one
`POST {private_base_url}/api/chat`. The body allowlist is `model`, `messages`,
`stream=false`, `format`, and `keep_alive`; there is no `options`, health
preflight, second request, retry, fallback, provider SDK, or internally created
client.

The effective timeout is exactly
`min(request.timeout_ms, config.timeout_ceiling_ms)`, enforced across HTTP
phases and a total async operation deadline. Caller cancellation propagates.
