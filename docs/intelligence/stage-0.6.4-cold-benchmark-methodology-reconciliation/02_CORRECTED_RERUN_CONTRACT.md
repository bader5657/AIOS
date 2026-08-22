# Corrected Cold Rerun Contract

## Sole permitted prompt correction

Use the same synthetic record and instruction used by the first cold request,
with only this exact sentence added:

```text
confidence must be a decimal number between 0.0 and 1.0, never a percentage.
```

No other prompt editing is authorized.

## Frozen execution controls

The rerun must use:

- Ollama `0.32.13`;
- `qwen2.5:1.5b-instruct-q4_K_M`;
- the same synthetic record;
- the same object schema: category `normal | warning`, confidence numeric
  `0.0..1.0`, no additional properties;
- non-streaming output;
- temperature `0`;
- seed `42`;
- context `512`;
- maximum predicted tokens `32`;
- concurrency `1`, queue `1`, retry `NONE`;
- memory `3,221,225,472` bytes, memory+swap `3,221,225,472` bytes,
  `NanoCpus=1,000,000,000`, and the existing `120000 ms` ceiling.

Exactly one corrected cold rerun is authorized. This adds one bounded
methodology-validation request to the historical execution record; it does not
alter the official twenty-warm sampling plan or its percentile rules.

After the corrected response, stop request generation, run the required
read-only post-checks, validate without coercion, preserve all evidence, and
return the result for governance review. Do not begin warm requests
automatically.
