# Benchmark Request, Schema, and Sampling

## Synthetic-data policy

Every request must use the exact synthetic record below. Production business
data, Telegram content, secrets, credentials, customer/order data, and copied
production payloads are prohibited.

```text
Classify this synthetic event. Return only JSON matching the supplied schema.
Event: {"source":"lab-sensor","reading":17,"threshold":20}
Use category "below" when reading is below threshold, otherwise "at_or_above".
Set confidence to 1.
```

## Fixed structured-output contract

The request must use Ollama's non-streaming structured `format` field with this
exact schema:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["category", "confidence"],
  "properties": {
    "category": {
      "type": "string",
      "enum": ["below", "at_or_above"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    }
  }
}
```

The expected semantic result is
`{"category":"below","confidence":1}`. A response passes only if it is one
JSON object, validates against the schema, contains no extra properties, and
has the expected semantic values.

## Deterministic request controls

| Setting | Approved value |
|---|---|
| API | local isolated runtime `/api/generate` only |
| Streaming | `false` |
| Temperature | `0` |
| Seed | `42` |
| Context | `512` tokens |
| Output | `32` predicted tokens maximum |
| Keep-alive | existing `5m` |
| Concurrency | exactly `1` |
| Retry | `NONE` |
| Per-request ceiling | `120000 ms` |

No open-ended quality, throughput, parallelism, long-context, production-data,
tool-use, embedding, or conversational benchmark is authorized.

## Sampling sequence

1. Capture the complete pre-load baseline.
2. Execute exactly one normal cold request and measure load plus total latency.
3. After successful cold completion, execute exactly `20` identical normal
   warm requests serially.
4. Execute one controlled adversarial/syntax stress request.
5. Execute one controlled client-timeout request.
6. Stop request generation, observe configured keep-alive expiry, and verify
   unload and recovery.

The maximum approved request count is `23`. A stopped or failed run must not be
resumed or padded with replacement requests without a new execution decision.
