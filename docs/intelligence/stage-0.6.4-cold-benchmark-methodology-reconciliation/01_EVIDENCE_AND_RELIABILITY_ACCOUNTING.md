# Evidence and Reliability Accounting

## Permanent first-cold record

Record the first cold result as follows:

- runtime: Ollama `0.32.13`;
- model: `qwen2.5:1.5b-instruct-q4_K_M`;
- HTTP: `200`;
- latency: `5953 ms`;
- content: `{"category":"normal","confidence":100}`;
- schema conformance: `FAIL`;
- classification: `CONTAINED_INVALID_RESULT`.

The raw response, request, timestamps, resource samples, validator rejection,
and interrupted shell outcome remain immutable benchmark evidence.

## Conservative denominator

The official normal-result reliability denominator remains exactly `21`:

1. the original invalid cold result; and
2. the official twenty warm requests, if separately authorized and executed.

The corrected cold rerun is additional methodology-validation evidence. It is
reported independently and is not substituted for the invalid first cold
result, does not reset the denominator, and does not increase the number of
official warm samples.

Consequently, `PASS_FOR_DEVELOPMENT` is no longer reachable in this benchmark
record. `PASS_WITH_LIMITATION` remains reachable only if the corrected cold
rerun is valid, all twenty later-authorized warm results are valid, and every
remaining safety, latency, malformed-output, timeout, unload, and recovery gate
passes. The maximum official normal reliability is `20/21` (`95.24%`).

An invalid corrected cold rerun ends rerun authority immediately. No repeated
rerun, repair, coercion, replacement, or denominator reset is permitted; return
the complete evidence to governance classification.
