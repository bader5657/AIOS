# README Disposition and Accepted Capability Ledger

## Current production-operational foundation

README now accurately limits current production evidence to the accepted Stage
9 foundation: systemd-managed host operation, enabled active service, approved
runtime virtualenv, reboot activation, exactly one Telegram poller,
loopback-only PostgreSQL endpoint, read-only separated source, protected
runtime configuration/data/cache, security/exclusion boundaries, and
systemctl/journald operational surfaces.

## Bounded component evidence

| Component | Accepted README disposition |
|---|---|
| Telegram / Universal Ingestion | Transport, one production poller, bounded delegation, RequestContext/lifecycle handoffs, and receipt/readiness acknowledgement; no autonomous response or business completion |
| Storage / Metadata / Manifest | Original-file storage, bounded metadata extraction, and Manifest creation after approved processing; not a generalized storage or intelligence platform |
| PostgreSQL Registry | Bounded persistence, Registry-local transaction ownership, commit/rollback, and pipeline integration; no generalized automation, ORM platform, retry, pooling capability, or deduplication |
| Event Engine | Async in-process EventEnvelope processing, bounded outcomes, and Registry-before-Event ordering; no broker, queue, durable ledger, retry, or distributed dispatch |
| AIOS Core | Stateless deterministic async EventEnvelope routing readiness; sole positive target `AIOS_BRAIN_BOUNDARY`; no Brain, LLM, reasoning, or business completion |
| Asset Pipeline | Lifecycle verified in approved ingestion/storage/metadata/Manifest scope; not whole-product completion |
| Mission Control | Status/version/environment and bounded image/Manifest inventory formatter only; not operational health, monitoring platform, or command center |

## Broad wording dispositions

- `Foundation Completed`: removed; replaced by bounded Stage 5–9 foundation
  wording.
- `Asset Pipeline Completed`: narrowed to its accepted lifecycle scope.
- `Mission Control Completed`: narrowed to verified formatter behavior.
- Telegram Bot breadth: replaced by transport/poller/ingestion acknowledgement
  wording.
- stale immediate Next Milestone list: removed; future work follows the active
  frozen execution plan without speculation.

## Later-stage classifications

- Brain: `LATER-STAGE / UNVERIFIED`
- Intelligence/LLM: `LATER-STAGE / UNVERIFIED`
- Memory: `LATER-STAGE / UNVERIFIED`
- Specialist Router/Specialists: `LATER-STAGE / UNVERIFIED`
- business-management capabilities: `ROADMAP / UNVERIFIED`
- broader autonomous automation: `UNVERIFIED`; only accepted systemd lifecycle
  operation is current
