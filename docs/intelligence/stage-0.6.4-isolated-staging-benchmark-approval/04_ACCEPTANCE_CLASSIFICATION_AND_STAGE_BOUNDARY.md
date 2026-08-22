# Acceptance Classification and Stage Boundary

## PASS_FOR_DEVELOPMENT

Classify `PASS_FOR_DEVELOPMENT` only when all of the following hold:

- every production safety gate remains stable and the host remains responsive;
- container RAM never breaches `3 GiB`, CPU remains capped at `1 vCPU`, no OOM
  or restart occurs, and swap/disk policies pass;
- cold request completes within `120000 ms` and warm p95 is at most `30000 ms`;
- all `21/21` normal outputs are JSON-, schema-, and semantically valid;
- malformed output is detected and contained fail-closed;
- timeout behavior is bounded, recoverable, non-retrying, and classified
  `FailureCode.TIMEOUT` at the benchmark boundary;
- model unloads within `7m` and memory recovery meets the approved threshold.

This result means the current KVM2 environment is safe and workable for
continued isolated AIOS Intelligence development only.

## PASS_WITH_LIMITATION

Classify `PASS_WITH_LIMITATION` only when every safety, limit, swap, disk,
timeout-recovery, containment, and unload gate passes, but either:

- warm p95 exceeds `30000 ms` while every normal request remains below
  `120000 ms`; or
- exactly one normal result is invalid but contained, producing at least
  `20/21` (`95.24%`) normal structured-output success.

The limitation must be recorded explicitly. This result means the runtime is
safe and functional for bounded development, but its latency or reliability is
not sufficient to support a production-quality claim.

## FAIL

Classify `FAIL` on any production instability or stop condition; resource,
swap, disk, isolation, or responsiveness failure; cold or ordinary request at
the `120000 ms` ceiling; fewer than `20/21` valid normal outputs; repeated or
uncontained malformed output; unusable timeout/cancellation behavior; runtime
non-recovery; unload failure; or material RAM non-recovery.

A failed benchmark returns to runtime/provider strategy governance. It does not
authorize retries with wider limits, another model, or production changes.

## Production meaning and next-stage mapping

Neither pass classification authorizes production Brain integration,
production inference, service wiring, traffic, secrets, startup automation, or
deployment. Production authority remains `NONE`.

After `PASS_FOR_DEVELOPMENT` or `PASS_WITH_LIMITATION`, the next candidate is a
separate governance evaluation of the first real Ollama provider adapter and
Brain integration boundary. After `FAIL`, return to runtime/provider strategy
governance.
