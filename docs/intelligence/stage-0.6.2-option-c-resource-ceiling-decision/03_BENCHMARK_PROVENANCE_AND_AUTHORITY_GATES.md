# Benchmark, Provenance, and Authority Gates

## Production and acquisition authority

Production authority remains `NONE`. This decision authorizes controlled
staging preparation governance only. It does not authorize:

- installing or pulling Ollama;
- acquiring or downloading any model;
- executing a container or inference;
- connecting the candidate provider to production Brain orchestration;
- modifying `aios.service`, AIOS source, PostgreSQL, Telegram, production
  Docker state, dependencies, configuration, or Core Platform behavior;
- production activation or production inference.

Stage 0.6.3 must separately define and approve the exact Docker image and
digest, exact model manifest and digest, exact storage path, exact bounded
16 GiB filesystem, RAM and CPU container limits, private or loopback network,
model acquisition procedure, cleanup and rollback, and benchmark procedure.

## Required benchmark

Before any production decision, staging evidence must measure:

- cold startup and warm state;
- idle, peak, and steady RAM;
- CPU saturation and swap usage;
- disk footprint;
- p50 and p95 latency and timeout behavior;
- structured-output success rate and schema conformance;
- malformed-output containment and failure mapping;
- service isolation.

The benchmark is `FAIL` if the runtime exceeds `3 GiB` RAM; sustained or
model-attributable swap occurs; AIOS, PostgreSQL, or Telegram polling becomes
unstable; host responsiveness is materially degraded; structured output is
unreliable; or isolation boundaries fail.

## Provenance blocker

Canonical Qwen-to-Ollama artifact provenance reconciliation remains required
before installation authority. The exact canonical Qwen revision must be tied
to the exact Ollama manifest/artifact and verified digest. This blocker is not
resolved or waived by the disk-ceiling decision.
