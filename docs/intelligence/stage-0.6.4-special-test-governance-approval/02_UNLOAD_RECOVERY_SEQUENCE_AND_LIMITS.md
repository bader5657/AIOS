# Unload, Recovery, Sequence, and Limits

## Exact execution sequence

The activated authority must be executed in this order:

1. fresh read-only safety preflight;
2. exactly one timeout test;
3. safety post-check;
4. exactly one malformed-output containment test;
5. safety post-check;
6. unload/recovery observation; and
7. final production/resource state capture.

No additional normal inference request is authorized.

## Unload and memory recovery

After the inference-related tests complete, send no keep-alive override and
observe the configured keep-alive behavior. Poll `/api/ps` read-only. The model
must become absent within the already approved unload observation window of
seven minutes after the final inference response.

After unload, container memory must return to within `256 MiB` of the recorded
pre-load/runtime baseline within the already approved additional two-minute
recovery window. Record time-to-unload and memory recovery. AIOS, PostgreSQL,
and the single Telegram poller must remain stable. Do not restart the container
or any production service merely to force unload or recovery.

## Frozen resource and execution controls

- container RAM: `3 GiB`;
- CPU: `1 vCPU`;
- concurrency: `1`;
- queue: `1`;
- runtime timeout ceiling: `120000 ms`;
- retry: none;
- fallback: none; and
- dynamic routing: none.

The runtime and model remain Ollama `0.32.13` and
`qwen2.5:1.5b-instruct-q4_K_M`. Synthetic data only is permitted.
