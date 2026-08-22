# Prohibitions, Cleanup, and Production Isolation

## Prohibited actions

This authority does not permit:

- pulling `qwen2.5:1.5b-instruct-q4_K_M` or any other model;
- starting `ollama serve` or any process from the image;
- model loading, inference, API exposure, or health execution that starts the
  runtime;
- installing Ollama into AIOS production;
- modifying AIOS source, runtime data, `aios.service`, PostgreSQL, Telegram,
  production compose topology, existing workloads, or unrelated images;
- creating production runtime authority;
- changing any Stage 0.6.1 resource ceiling.

The measurement may retrieve only the exact pinned image layers into its
approved disposable, quota-controlled environment.

## Isolation and protected services

If any host-assisted method is later approved, record before/during/after
evidence that `aios.service`, PostgreSQL, Telegram polling, and existing Docker
workloads remain healthy and were neither stopped nor restarted. The operation
must stop before the host reserve is threatened.

The preferred design has no interaction with the production Docker store and
therefore no production-service lifecycle effect.

## Cleanup

After evidence collection, remove only the temporary daemon/data-root,
retrieved image content, snapshots, non-running container metadata, and other
artifacts created by this measurement. Do not prune or alter the production
Docker store or unrelated files.

Post-cleanup evidence must show:

- the disposable environment is absent;
- temporary disk usage is released;
- the host reserve remains satisfied;
- repository and protected services are unchanged;
- no Ollama process, model, public endpoint, or production artifact remains.

Disk evidence alone cannot close Stage 0.6.2. Canonical Qwen revision to Ollama
artifact provenance reconciliation remains a separate approval prerequisite.
