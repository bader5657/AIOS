# Baseline, Accepted Verification Ledger, and Closed Scope

## Exact baseline

- `HEAD == main == origin/main` at approval start:
  `5dc7e504240a168b5acf466be1e23efd9b6f9b1d`
- Worktree: `CLEAN`
- Stage 9.2.4 closure baseline:
  `5dc7e504240a168b5acf466be1e23efd9b6f9b1d`

## Accepted verification ledger

| Capability | Accepted evidence | Exact scope and limitation |
|---|---|---|
| PostgreSQL Registry persistence | Stage 5 | Registry-local persistence and transaction/failure behavior; no generalized retry, pooling, ORM, deduplication, or binary storage |
| Manifest → Registry | Stage 5.4.1 | Bounded integration after Manifest readiness; initially verified with isolated PostgreSQL |
| Event Engine | Stage 6 | Async, in-process, in-memory, sequential dispatch; no broker, persistence, or automatic retry |
| Registry → Event Engine | Stage 6.3.2 | Registry commit precedes caller-owned event processing |
| AIOS Core | Stage 7 | Stateless deterministic EventEnvelope routing readiness to `AIOS_BRAIN_BOUNDARY`; no Brain invocation |
| Telegram → Universal Ingestion | Stage 8.1.1 | Transport delegation and receipt/readiness acknowledgement; not semantic business completion |
| RequestContext → Asset Pipeline → Manifest | Stage 8.1.2 | Ownership and ordering verification; bounded component integration |
| Manifest → Registry → Event Engine | Stage 8.1.3 | Commit and ordering integration evidence |
| Event Engine → AIOS Core | Stage 8.1.4 | Same-envelope route call after Event success; stops at Brain boundary |
| Official lifecycle and failures | Stages 8.2.1 and 8.4.1 | Bounded lifecycle order, suppression, and preservation; no cross-component transaction, retry, compensation, or deduplication |
| systemd production operation | Stages 9.1–9.2.2 | Enabled active host process, reboot activation, approved runtime venv, exactly one Telegram poller, systemctl/journald surfaces |
| PostgreSQL production placement | Stages 9.2.2–9.2.4 | Loopback-only endpoint and data outside source; no claim of generalized database automation |
| Source/runtime and security separation | Stages 9.2.3–9.2.4 | Source read-only; runtime, data, cache, secrets, rollback, and protected data structurally outside source/Git |

## Closed-world future implementation scope

Exactly these two paths are authorized for the later implementation:

1. `README.md`
2. `CHANGELOG.md`

No third path is authorized. If any other file appears necessary, execution
must stop with:

`STAGE 9.3.1 DOCUMENTATION SCOPE EXPANSION REQUIRED`
