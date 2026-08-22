# Proposed Installation, Rollback, and Benchmark Handoff

## Preconditions

Future execution must prove before mutation that:

- the exact 16 GiB bound can be enforced;
- host reserve remains at least `max(10 GiB, 15% of filesystem capacity)`;
- production Docker free space remains safe;
- no pre-existing swap or resource instability exists;
- RAM and CPU container limits are enforceable; and
- the provenance blocker has been closed by a separate governance record.

## Exact future sequence

1. capture production-state read-only prechecks;
2. create the bounded staging filesystem and exact owned directories;
3. create staging-only Docker configuration and loopback/private networking;
4. acquire only the pinned Ollama image;
5. verify platform and full image digest;
6. create the isolated container without production integration;
7. start only the runtime;
8. verify bounded runtime readiness without model loading;
9. acquire only the exact model manifest and blob approved after provenance;
10. verify manifest, blob digest, size, quantization, license, and provenance;
11. stop the runtime or ensure the model is unloaded if benchmark has not begun;
12. collect post-install disk, resource, network, and protected-service state.

This sequence is not authorized by this blocked evaluation.

## Rollback

Rollback may remove only the named staging container, its staging-only network
objects, the bounded staging filesystem/config, and model data below the exact
runtime root. It must not prune or alter production Docker images, volumes,
networks, containers, services, source, secrets, PostgreSQL, or Telegram.

## Stop conditions

Stop on provenance mismatch or ambiguity; insufficient host reserve; inability
to enforce the 16 GiB, 3 GiB RAM, or one-vCPU limits; required public exposure;
required production secrets; any required change to `aios.service`, PostgreSQL,
or Telegram; required provider-adapter work; or any need for another model.

## Integration and benchmark boundary

No Brain, `InferenceProvider`, AIOS Core, or Telegram integration is included.
There is no systemd integration, automatic boot dependency, production
activation, inference authority, or production-readiness claim.

After a separately approved and successful installation, the next stage is:

`Intelligence Stage 0.6.4 — Ollama/Qwen Isolated Staging Benchmark`

The benchmark remains mandatory and separate from installation.
