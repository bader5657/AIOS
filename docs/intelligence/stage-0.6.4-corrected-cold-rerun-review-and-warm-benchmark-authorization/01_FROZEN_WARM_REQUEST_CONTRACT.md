# Frozen Warm Request Contract

## Request settings

Every authorized request must use the existing approved schema and synthetic
record with these unchanged controls:

- model: `qwen2.5:1.5b-instruct-q4_K_M`;
- runtime: Ollama `0.32.13`;
- temperature: `0`;
- seed: `42`;
- context: `512` tokens;
- maximum predicted tokens: `32`;
- stream: `false`;
- concurrency: `1`;
- RAM ceiling: `3 GiB`;
- CPU ceiling: `1 vCPU`;
- retry: `NONE`;
- fallback: `NONE`.

Use the prompt correction already validated by the corrected cold rerun:

```text
confidence must be a decimal number between 0.0 and 1.0, never a percentage.
```

The schema must not change. The clarified sentence describes the scale already
enforced by that schema; it does not amend the structured-output contract.

## Exact request count and serialization

Execute exactly `20` official warm requests. Run them sequentially with
concurrency `1`, no overlap, no replacement, no retry, and no additional
ordinary requests. A stopped, invalid, failed, or timed-out request remains in
the official record and must not be discarded or padded with another request.

This authorization starts from the current loaded-model state. It does not
authorize another cold request.
