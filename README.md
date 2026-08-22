# AIOS

Artificial Intelligence Operating System

Version: 0.1.0-alpha

## Current Verified Foundation

Stage 9 operational alignment has verified the systemd-managed Telegram/Core
Platform runtime foundation, single-poller operation, reboot activation,
source/runtime separation, and security/exclusion boundaries.

Current production-operational evidence covers:

- an enabled and active `aios.service` host process using the approved runtime
  Python virtual environment;
- automatic activation after reboot and exactly one Telegram polling process;
- a loopback-only PostgreSQL production endpoint;
- read-only production source separated from runtime configuration, data,
  rollback artifacts, business originals, Manifests, and generated cache;
- protected runtime configuration and Git exclusion boundaries; and
- `systemctl` and journald as the verified operational observability surfaces.

This operational foundation does not establish Brain, LLM, Memory, Specialist,
autonomous workflow, or completed business-management capability.

## Verified Components and Limits

- **Telegram and Universal Ingestion:** the Telegram transport adapter,
  production single poller, bounded delegation, `RequestContext` lifecycle,
  Storage/Metadata/Manifest flow, and receipt/readiness acknowledgement are
  verified. This is not arbitrary semantic understanding, autonomous response,
  web retrieval, or completed business workflow evidence.
- **Storage, Metadata, and Document Manifest:** original-file storage,
  bounded metadata extraction, and Document Manifest creation after approved
  storage and metadata processing are verified. These components are not a
  generalized storage or document-intelligence platform.
- **PostgreSQL Registry:** bounded persistence, Registry-local transaction
  ownership, commit/rollback behavior, and approved pipeline integration are
  verified. No ORM platform, automatic retry, pooling capability,
  deduplication, or autonomous persistence orchestration is claimed.
- **Event Engine:** async in-process processing of approved `EventEnvelope`
  inputs, bounded handler outcomes, and Registry-before-Event ordering are
  verified. No broker, queue, durable event ledger, retry, or distributed
  dispatch is implemented.
- **AIOS Core:** the async routing boundary is stateless and deterministic,
  accepts an `EventEnvelope`, and returns bounded readiness with
  `AIOS_BRAIN_BOUNDARY` as its sole positive target. It does not invoke Brain,
  execute an LLM, reason, or complete business work.
- **Asset Pipeline:** lifecycle behavior is verified within the approved
  ingestion, storage, metadata, and Manifest scope. This is component evidence,
  not whole-product completion.
- **Mission Control:** verification covers its status/version/environment and
  bounded image/Manifest inventory formatter. Its static `Running` text is not
  service-health, readiness, monitoring-platform, or command-center evidence.

## Project Structure

```text
core/
    adapters/
    app/
    ingestion/
    mission/
    storage/
```

## Not Yet Verified / Later Stage

Brain execution, Intelligence or LLM runtime, reasoning, model selection,
Memory and knowledge retrieval, Specialist Router and Specialists, autonomous
workflows, business-management automation, n8n orchestration,
Hermes/OpenClaw, Ollama, brokers/queues, and generalized retry,
deduplication, or compensation are not current verified capabilities.

Customer, order, product, transaction, HPP, inventory, and reporting
automation remain later-stage work unless separately implemented and accepted.

## Roadmap Status

The Core Platform foundation is verified within its accepted Stage 5–9
scopes. This does not mean the full AIOS product or all roadmap phases are
complete. Next work follows the active frozen execution plan; later-stage
capabilities remain unverified until separately implemented and accepted.
