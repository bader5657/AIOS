# Orphans, Possible Exclusions, Deferral Preview, and Review

## Implementation without requirement trace

These findings are not automatically invalid and are not Included Scope gaps.

| Finding | Current path | Classification | Disposition for 10.1.1 |
|---|---|---|---|
| Customer concrete domain | `core/domain/customer/` | `IMPLEMENTATION_WITHOUT_REQUIREMENT_TRACE — FOUNDATION/RELEASE BASELINE, NOT CORE PLATFORM REQUIREMENT` | Retain as accepted Foundation; only shared DomainEvent/EventEnvelope contracts are consumed by this matrix |
| Package exports/internal helpers | `core/*/__init__.py`, private validators/name/path helpers | `IMPLEMENTATION_WITHOUT_REQUIREMENT_TRACE — HARMLESS INTERNAL REALIZATION` | Covered transitively by owning public contracts; no independent capability claim |

`IMPLEMENTATION_WITHOUT_REQUIREMENT_TRACE FINDINGS = 2`

No finding demonstrates authority drift, later-phase execution, or an orphan
runtime capability requiring correction.

## Orphan requirements

No Included Scope row lacks current realization, accepted evidence, and an
accepted closure.

- no implementation: `0`
- no evidence: `0`
- no accepted closure: `0`
- candidate completion blocker: `0`

## Possible exclusions for Stage 10.1.2

The following are deliberately **not** formally excluded here. They appear
outside the approved Core Platform milestone and must receive exact authority
disposition in Stage 10.1.2.

| Candidate | 10.1.1 status | Why it is not concealing an Included Scope gap |
|---|---|---|
| Brain execution/reasoning | `POSSIBLE_EXCLUSION` | Core requirement ends at tested `AIOS_BRAIN_BOUNDARY`; CP-TRACE-074/076 covered |
| Intelligence/LLM | `POSSIBLE_EXCLUSION` | No Core requirement calls an LLM; absence verified by boundaries |
| Memory/Knowledge runtime | `POSSIBLE_EXCLUSION` | Not consumed by current bounded Core route |
| Specialist Router/Specialists | `POSSIBLE_EXCLUSION` | Downstream of Brain in Blueprint; no current execution |
| Business workflow/runtime | `POSSIBLE_EXCLUSION` | Roadmap later phase; adapter response is not business completion |
| Autonomous automation | `POSSIBLE_EXCLUSION` | Systemd lifecycle operation is the only current automation claim |
| n8n/Hermes/OpenClaw/Ollama runtime | `POSSIBLE_EXCLUSION` | No current Core authority or coupling |
| Broker/queue/distributed Event infrastructure | `POSSIBLE_EXCLUSION` | Accepted Event Engine is explicitly in-process |
| Generalized retry/deduplication/compensation | `POSSIBLE_EXCLUSION` | Accepted component contracts explicitly define none/bounded behavior |

`POSSIBLE_EXCLUSION = 9`

## Zero-hidden-deferral preview

Items requiring explicit 10.1.2 carry-forward review, without disposition here:

- journald contextual Telegram metadata privacy hardening;
- PostgreSQL host UID/GID display observation;
- rollback root mode and document root mode observations;
- predecessor/runtime rollback retention;
- Telegram SDK coupling and Mission status out-of-pipeline behavior;
- arbitrary mid-copy partial-destination cleanup limitation;
- non-transactional effects of earlier successful Event handlers;
- absence of generalized retry/deduplication/compensation; and
- all nine possible-exclusion candidates above.

None is used to cover a missing Included Scope implementation. The exact
accepted limitation is visible in the corresponding `COVERED_WITH_LIMITATION`
row.

## Coverage reconciliation

| Area | Included | Covered | Covered with limitation | Gap | Ambiguous |
|---|---:|---:|---:|---:|---:|
| Adapter/Telegram | 7 | 4 | 3 | 0 | 0 |
| RequestContext | 6 | 4 | 2 | 0 | 0 |
| Universal Ingestion/Asset Pipeline | 14 | 8 | 6 | 0 | 0 |
| Storage/Metadata/Manifest | 18 | 13 | 5 | 0 | 0 |
| Registry/PostgreSQL | 13 | 8 | 5 | 0 | 0 |
| Domain Foundation | 4 | 4 | 0 | 0 | 0 |
| Event Engine | 8 | 4 | 4 | 0 | 0 |
| AIOS Core | 7 | 6 | 1 | 0 | 0 |
| Lifecycle/failure | 6 | 0 | 6 | 0 | 0 |
| Operational/source-runtime/observability | 7 | 6 | 1 | 0 | 0 |
| Security/exclusion | 7 | 5 | 2 | 0 | 0 |
| Documentation/capability | 5 | 5 | 0 | 0 | 0 |
| Mission/Registry/config/operational completeness | 6 | 4 | 2 | 0 | 0 |
| **Total** | **108** | **71** | **37** | **0** | **0** |

The grouped totals reconcile exactly with the row-level matrix. Stage 10.1.1
is complete on the traceability baseline. Stage 10.1.2 has not begun.
