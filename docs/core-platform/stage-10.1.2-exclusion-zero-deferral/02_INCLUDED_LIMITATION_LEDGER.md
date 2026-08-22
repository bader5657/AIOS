# Included Scope Accepted-Limitation Ledger

Every `COVERED_WITH_LIMITATION` row remains Included Scope. None is reclassified as excluded or deferred required functionality.

| Requirement ID | Limitation | Authority / accepted stage | Why requirement remains complete | Future hardening/owner |
|---|---|---|---|---|
| CP-TRACE-001 | Telegram SDK coupling accepted | BP; EP; owner 8.1.1/8.2.1; Stage 8.1.1 closure; C9 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Telegram owns transport receipt | Future adapter abstraction |
| CP-TRACE-003 | Acknowledgement is receipt/readiness, not business completion | EP; owner 8.1.1/8.2.1; Stage 8.1.1/8.2.1 closures | Implementation/evidence/closure chain is complete for the explicit bounded contract: Adapter acknowledgement only after bounded readiness | Later business response |
| CP-TRACE-004 | Accepted Mission status out-of-pipeline behavior | BP; LA; EP; owner 8.3.1; Stage 8.3.1 closure; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Adapter does not own pipeline semantics | Separate helper cleanup |
| CP-TRACE-010 | Fields are transport context, not business identity | BP; EP; owner 2.2.1; Stage 2.2.2 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: RequestContext contains source/user/chat/message/username/text/time | Later business identity |
| CP-TRACE-012 | Contextual identifiers retained where authorized | EP; Canonical Model; owner 2.1.2; Stage 2.2.2; C3 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Telegram identifiers are not promoted to domain/business identity | Later canonical identity |
| CP-TRACE-015 | PDF/DOC/spreadsheet and links map to compatible primitive pipeline paths | BP; EP; owner 3.1; C3 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Classify all ten Blueprint input families | Later rich format processing |
| CP-TRACE-019 | No default domain-event synthesis | EP; owner 6.3.2/8.1.3; Stage 6.3.2; Stage 8.1.3 closures | Implementation/evidence/closure chain is complete for the explicit bounded contract: Event Engine invocation is optional and gated after Registry commit | Later domain-event creation |
| CP-TRACE-020 | No Brain call | EP; owner 8.1.4; Stage 8.1.4 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: AIOS Core invocation is optional and gated after Event success | Brain phase |
| CP-TRACE-021 | `process_handoff_ready` remains conservative false; detailed Event fields are authoritative | EP; owner 3/8; C3; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Ingestion result exposes bounded handoff/readiness outcomes | No implicit business readiness |
| CP-TRACE-023 | Transport-local result is non-canonical | EP; owner 4; C4 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Asset Pipeline is bounded/stateless orchestration | Separate canonical authority |
| CP-TRACE-024 | File-only storage step; text/URL have no original file | BP; EP; owner 4; C4 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Pipeline order is Store → Metadata → Manifest | None required |
| CP-TRACE-029 | Arbitrary mid-copy partial destination cleanup not guaranteed | EP; owner 3.2; C3 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Original bytes stored exactly once without overwrite/retry | Future Storage hardening |
| CP-TRACE-031 | Telegram SDK coupling accepted | EP; owner 3/8; C3; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Telegram download ownership is Storage-local | Future adapter abstraction |
| CP-TRACE-032 | Temporary-download cleanup only | EP; owner 4/8; C4; Stage 8.4.1 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: Storage failure suppresses Metadata/Manifest/downstream | Future Storage hardening |
| CP-TRACE-040 | Telegram IDs are contextual only | EP; owner 3.4.1; Stage 3.4.2 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: Manifest constructed from authorized context/media/metadata/reference fields | Later identity semantics |
| CP-TRACE-043 | Context only; not business identity | EP; owner 3.4.1; Stage 3.4.2 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: Manifest records authorized Telegram context identifiers | Later identity semantics |
| CP-TRACE-046 | Row is database-local, non-canonical | BP; EP; owner 5; Stage 5.3.2 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: Registry persists five authorized categories | Canonical Registry Entry authority |
| CP-TRACE-048 | No pool/ORM platform | EP; owner 5.3.1; Stage 5.3.2 closure | Implementation/evidence/closure chain is complete for the explicit bounded contract: Registry owns one local connection/transaction per operation | Future performance/platform work |
| CP-TRACE-054 | Duplicate behavior remains caller/domain concern | EP; owner 5; Stage 5.3.2; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Registry adds no dedup/idempotency/domain uniqueness | Future domain-specific authority |
| CP-TRACE-057 | Repository compose uses external network; production placement evidence is authoritative | BP; EP; owner 9.2.2; Stage 9.2.2; C9 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Production PostgreSQL endpoint is loopback-only | Operational review |
| CP-TRACE-058 | Host UID/GID display observation retained | BP; EP; owner 9.2.4; Stage 9.2.4; C9 | Implementation/evidence/closure chain is complete for the explicit bounded contract: PostgreSQL data remains outside source/Git | Later operations/security review |
| CP-TRACE-064 | Earlier successful handler effects remain on later failure | EP; owner 6.3/6.4; Stage 6.4.1; C6 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Handlers execute sequentially in registration order from snapshot | Future transaction/compensation design |
| CP-TRACE-066 | Earlier handler side effects not compensated | EP; owner 6.4.1; Stage 6.4.1; C6 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Invalid envelope/no handler/handler failure are contained | Future compensation authority |
| CP-TRACE-068 | No distributed delivery guarantee | EP; owner 6/8; C6; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Event Engine has no broker/queue/durable ledger | Future architecture |
| CP-TRACE-069 | Each explicit invocation may deliver again | EP; owner 6/8; Stage 6.4.1; Stage 8.4.1 closures | Implementation/evidence/closure chain is complete for the explicit bounded contract: Event Engine performs no automatic retry/dedup/compensation | Future retry/idempotency authority |
| CP-TRACE-074 | Boundary marker only | EP; Project Owner direction; owner 7; Stage 7.3.1; C7 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Exactly one positive target is `AIOS_BRAIN_BOUNDARY` | Brain phase |
| CP-TRACE-078 | Applicable file storage only; readiness response only | BP; EP; owner 8.2.1; Stage 8.2.1; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Official sequence is Receive→Context→Store/Metadata/Manifest→Registry→Event→Core→Respond | Later business completion |
| CP-TRACE-079 | Accepted SDK coupling does not transfer semantics | EP; owner 8.2.1/8.3.1; Stage 8.2.1/8.3.1 closures | Implementation/evidence/closure chain is complete for the explicit bounded contract: Component ownership remains separated across lifecycle | Future decoupling |
| CP-TRACE-080 | Earlier handler effects remain | EP; owner 8.4.1; Stage 8.4.1; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Failure suppresses every downstream stage | Future compensation design |
| CP-TRACE-081 | No arbitrary mid-copy cleanup/distributed rollback | EP; owner 8.4.1; Stage 8.4.1; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Failure preserves every completed upstream artifact/state | Future resilience design |
| CP-TRACE-082 | Event handler side effects non-transactional | EP; owner 8.4.1; Stage 8.4.1; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: No cross-component transaction or downstream rollback of upstream work | Future architecture |
| CP-TRACE-083 | No generalized resilience platform | EP; owner 8.4.1; Stage 8.4.1; C8 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Retry/compensation/dedup remain absent unless component contract explicitly states otherwise | Separate resilience authority |
| CP-TRACE-090 | Contextual Telegram metadata privacy hardening deferred | BP; EP; owner 9.2.2; Stage 9.2.2; C9 | Implementation/evidence/closure chain is complete for the explicit bounded contract: systemctl/journald provide operational visibility | Later privacy hardening |
| CP-TRACE-093 | journald privacy finding retained | BP; EP; owner 9.2.4; Stage 9.2.4; C9 | Implementation/evidence/closure chain is complete for the explicit bounded contract: DB dumps/backups/log files are excluded from Git/source | Later privacy hardening |
| CP-TRACE-094 | Root mode/retention observations remain | EP; owner 9.2.4; Stage 9.2.4; C9 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Rollback artifacts remain outside source | Later operations/security review |
| CP-TRACE-103 | Formatter only; not health monitoring or command center | EP; owner 1.4.2; Stage 1.4.2 accepted verification | Implementation/evidence/closure chain is complete for the explicit bounded contract: Mission Control provides bounded status/version/environment and inventory formatting | Future monitoring capability |
| CP-TRACE-106 | Retained historical/non-runtime artifact | EP; owner 6.1.1/6 exit; C6 | Implementation/evidence/closure chain is complete for the explicit bounded contract: Event Engine JSON schema is retained without becoming active runtime authority | Future config authority if needed |

`INCLUDED_WITH_ACCEPTED_LIMITATION = 37`

## None-semantics decision

- CP-TRACE-053: Registry automatic retry = `NONE`;
- CP-TRACE-054: Registry generalized dedup/idempotency = `NONE`;
- CP-TRACE-069: Event automatic retry/dedup/compensation = `NONE`;
- CP-TRACE-082: cross-component transaction/distributed rollback = `NONE`;
- CP-TRACE-083: generalized resilience platform = `NONE`.

`INCLUDED_REQUIREMENT_SATISFIED_BY_NONE_SEMANTICS = PASS`
