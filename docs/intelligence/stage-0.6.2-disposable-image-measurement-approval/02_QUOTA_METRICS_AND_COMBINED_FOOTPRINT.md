# Quota, Measurements, and Combined-Footprint Decision

## Hard limits

The disposable measurement filesystem/data-root must have an enforceable hard
maximum of `6 GiB` (`6,442,450,944 bytes`). The procedure must fail closed
before exceeding it. The following existing ceilings remain unchanged:

- runtime RAM: `3 GiB`;
- CPU: one vCPU equivalent;
- model file: `2 GiB`;
- runtime/model/temporary disk: `6 GiB`;
- concurrent inference: one;
- pending queue: one;
- timeout: `120000 ms`.

The host must retain at least `10 GiB` or 15 percent of filesystem capacity,
whichever is greater, throughout the measurement. The host reserve is not part
of, and does not enlarge, the 6 GiB AIOS staging budget.

## Required evidence

Record in bytes:

- before, peak, post-acquisition, and post-cleanup filesystem usage;
- verified manifest and configuration digests;
- every compressed layer digest and size and their total;
- content-store bytes;
- extracted snapshot/rootfs bytes;
- image and storage-driver metadata bytes;
- writable-layer/container metadata, only if a non-running container object is
  needed for measurement;
- storage backend and measurement commands/methodology.

No container process may be started. Creating a non-running container object is
allowed only when essential to quantify metadata, and it must be removed.

## Combined arithmetic

The already verified model-side persistence is fixed at `986,061,892 bytes`.
The approved runtime allowance is `128 MiB` (`134,217,728 bytes`). The Qwen
model must not be downloaded during this measurement.

Persistent combined footprint:

`measured Ollama persistent bytes + 986,061,892 + 134,217,728`

Acquisition-peak combined footprint:

`measured Ollama acquisition-peak bytes + 986,061,892 + 134,217,728`

The model component uses its verified persistent footprint. A second complete
model copy must not be assumed unless a later model-acquisition mechanism
demonstrably requires it.

## Classification

- `PASS`: both formulas are at most `6,442,450,944 bytes`.
- `CONDITIONAL_PASS`: persistent storage fits and a documented, enforceable
  acquisition procedure keeps peak usage within the same limit.
- `FAIL`: either unavoidable persistent or acquisition-peak usage exceeds the
  limit.

Unknown or unmeasured required values cannot produce PASS. The ceiling must not
be raised automatically.
