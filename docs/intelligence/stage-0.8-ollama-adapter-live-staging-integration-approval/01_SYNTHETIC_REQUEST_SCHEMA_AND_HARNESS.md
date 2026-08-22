# Synthetic Request, Schema, and Operator Harness

## Exactly one request

The controlled execution is limited to one invocation. There is no loop, retry, fallback, alternate model, alternate provider, or second inference request.

The identifiers are synthetic and fixed for the execution evidence:

- `correlation_id`: `stage-0.8-live-1`
- `request_id`: `stage-0.8-live-request-1`
- capability: `STRUCTURED_INFERENCE`
- `output_schema_ref`: `stage_0_8_sensor_classification_v1`
- request timeout: 120000 ms

## Input payload

The exact provider-neutral payload is:

```json
{
  "instruction": "Classify the synthetic sensor state. Return category normal when reading is below threshold; otherwise return warning. Confidence must be a number between 0.0 and 1.0.",
  "data": {
    "reading": 17,
    "source": "stage-0.8-synthetic-sensor",
    "threshold": 20
  }
}
```

It contains no Telegram, customer, order, transaction, business, secret, credential, production-identifier, provider-native, model, runtime, tool, session, or persistence data.

## Static output schema

The resolver accepts only `stage_0_8_sensor_classification_v1` and returns this bounded schema:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["category", "confidence"],
  "properties": {
    "category": {"type": "string", "enum": ["normal", "warning"]},
    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
  }
}
```

The operator-side independent validator must separately enforce:

- the parsed result is a mapping with exactly `category` and `confidence`;
- `category` is exactly `normal` or `warning` and is `normal` for the fixed synthetic input;
- `confidence` is numeric but not Boolean, finite, and within 0.0–1.0;
- no coercion, repair, default insertion, or provider response substitution occurs.

The provider-side `format` constraint remains defense in depth and is not the independent validator.

## Smallest execution method

Use one temporary operator-side Python invocation, held outside the repository or under `/tmp`, importing the accepted repository adapter and existing pinned `httpx==0.28.1`. It must:

1. construct the fixed `InferenceRequest`;
2. construct `OllamaProviderConfig` with `http://172.31.63.2:11434`, the fixed model, 120000 ms ceiling, and `5m` keep-alive;
3. inject one `httpx.AsyncClient`, the exact resolver, and the exact independent validator;
4. call `await provider.infer(request)` exactly once;
5. assert the approved result invariants without printing content;
6. emit only bounded metadata and PASS/failure status.

No harness is committed. No new dependency is installed. The adapter performs exactly one `POST /api/chat`; no `/api/version` health preflight or other adapter HTTP request is allowed.
