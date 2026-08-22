# Payload, Rendering, HTTP, Response, and Result

## Payload validation before side effects

An adapter-local private helper must validate before schema resolution or HTTP:

- top-level keys are exactly `instruction` and `data`;
- instruction is an exact string, 1–4096 characters, non-blank, and equal to
  its trimmed form;
- data is a mapping, including an allowed empty mapping; and
- no coercion, default, repair, unknown key, or provider-native top-level key
  is accepted.

Generic JSON compatibility, recursive immutability, depth/member bounds, and
the 1 MiB payload bound remain guaranteed by `InferenceRequest`. The adapter
does not reinterpret nested data keys as configuration.

## Deterministic rendering

Convert the immutable data snapshot to a detached plain JSON mapping, then
render exactly:

`instruction + "\n\nInput JSON:\n" + canonical_json(data)`

where canonical JSON is equivalent to:

```python
json.dumps(
    plain_data,
    ensure_ascii=False,
    allow_nan=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

The provider request contains exactly one message with exactly role `user` and
that content. There is no system message, assistant/history message, multi-turn
state, or session.

## Exact Ollama operation

Using the constructor-injected `httpx.AsyncClient`, execute exactly one async:

`POST {normalized_base_url}/api/chat`

The JSON body contains exactly:

- `model`: configured exact model ID;
- `messages`: the one user message;
- `stream`: `false`;
- `format`: detached resolved approved schema; and
- `keep_alive`: configured `5m`.

Do not include `options`, health/version preflight, retry, fallback, tools,
credentials, or any other provider field. Temperature, seed, `num_ctx`, and
`num_predict` remain deferred policy and runtime defaults, not adapter or
payload semantics.

The effective HTTP timeout is exactly
`min(request.timeout_ms, config.timeout_ceiling_ms)` and covers connection,
request, response headers, bounded body read, and parsing for the single
operation.

## Response and result

Measure duration locally with a monotonic clock and clamp only to the approved
`InferenceResult` duration bound if clock conversion would exceed it. Limit the
raw response body to at most `1_048_576` bytes; an oversized body is contained
as `MALFORMED_OUTPUT`.

Require a successful HTTP status and a JSON object envelope containing:

- `model`: exact configured model string;
- `done`: exact `true`; and
- `message`: a mapping containing string `content`.

Ignore and discard unrelated provider response fields. Model mismatch or
`done != true` is `PROVIDER_FAILURE`; malformed envelope types or missing/
invalid content are `MALFORMED_OUTPUT`.

Parse `message.content` with one strict JSON decode yielding exactly one
mapping. Trailing JSON tokens fail. Independently validate the mapping through
the injected validator. On success construct only `InferenceResult` with
`success=True`, no failure code, structured output present,
`provider_id="ollama-local"`, configured model ID, bounded duration, no failure
detail, and no raw provider data.

Raw request/response/error content is transient, never returned, persisted, or
logged, and is discarded on every path.
