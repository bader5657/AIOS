# Deterministic Rendering, Provider Settings, and Boundaries

## Exact rendering algorithm

After adapter-local validation, the adapter constructs exactly one
provider-native user-message content string:

`instruction + "\n\nInput JSON:\n" + canonical_data_json`

`canonical_data_json` is produced from the immutable `data` mapping by:

```python
json.dumps(
    plain_data,
    ensure_ascii=False,
    allow_nan=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

The resulting request body is encoded as UTF-8 by the async HTTP client. There
is no pretty printing, locale-dependent rendering, trailing newline, implicit
system text, or punctuation variation. JSON object keys are sorted
recursively by `json.dumps(sort_keys=True)`.

For the first Ollama adapter, this content becomes exactly one item in
`messages`, with role `user`. There is no system message, assistant history,
multi-turn conversation, session, or provider-native message structure in
`input_payload`.

## Output schema

`output_schema_ref` remains a separate `InferenceRequest` field. It is not
duplicated into `input_payload`. The adapter resolves it through the separately
approved injected resolver, sends the resolved schema as provider-side defense
in depth, and independently validates parsed output through the injected
validator before success.

## Provider settings ownership

`temperature`, `seed`, `num_ctx`, and `num_predict` are prohibited in
`input_payload`. Stage 0.6.4 benchmark values are measurement controls, not
permanent inference semantics.

The first adapter implementation must omit the Ollama `options` object and use
the approved runtime/model defaults. No immutable config fields or policy seam
for these settings are added in the first implementation. A future need for
deterministic sampling/context/output controls requires separate Brain
inference-policy governance; it must not be inferred from this contract.

Deterministic rendering is guaranteed. Deterministic model output is not
claimed.

## Privacy, state, and business boundary

Instruction and data are private content. They must not be logged, included in
failure details, persisted, cached, retained as conversation/session history,
or exposed as raw provider content. Only the existing bounded metadata log
allowlist remains available.

This contract supplies representation semantics only. Future Brain/business
flows must separately authorize any data values they supply. It authorizes no
customer/order/HPP/transaction behavior, business action, automated decision,
tool, Specialist, Memory, or production use.

Core remains unchanged and stops at `AIOS_BRAIN_BOUNDARY`. The payload contract
adds no Core dependency or new architecture layer.
