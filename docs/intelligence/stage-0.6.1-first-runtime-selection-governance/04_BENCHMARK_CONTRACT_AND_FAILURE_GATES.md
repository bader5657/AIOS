# Benchmark Contract and Failure Gates

Production activation is prohibited until a separately authorized controlled
staging benchmark records and passes all required evidence.

## Runtime and resource evidence

- cold startup time;
- warm startup state and runtime health;
- idle, peak, and steady-state RAM;
- CPU saturation;
- runtime/model/temporary disk usage; and
- swap usage and swap I/O.

## Inference and contract evidence

- p50 and p95 inference latency;
- timeout behavior;
- exact single-concurrency/one-pending-request behavior;
- valid structured-output rate;
- independent schema conformance validation;
- malformed-output containment;
- exact approved `FailureCode` mapping; and
- raw-response containment.

Provider-native JSON/schema mode is helpful but never sufficient by itself.
AIOS must independently parse and validate output before constructing a
successful `InferenceResult`.

## Isolation evidence

The benchmark must demonstrate that inference runtime failure, timeout, OOM,
container stop, and rejected excess load do not stop or destabilize:

- `aios.service`;
- PostgreSQL; or
- Telegram polling.

## Mandatory swap/host failure rule

The benchmark fails if inference causes sustained swap usage, materially
attributable swap I/O, severe host responsiveness degradation, or AIOS/
PostgreSQL/Telegram instability. Swap-dependent operation cannot proceed to
production approval.
