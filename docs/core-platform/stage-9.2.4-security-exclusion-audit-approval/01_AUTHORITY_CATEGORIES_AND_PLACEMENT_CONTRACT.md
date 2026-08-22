# Authority, Protected Categories, and Placement Contract

## Authority chain

- Blueprint: `docs/AIOS_ARCHITECTURE_v1.md`
- Frozen Roadmap: `docs/AIOS_Roadmap_Frozen.md`
- Execution authority: `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1.md`
- Stage 9.1.1 service implementation contract
- Stage 9.1.2 systemd service policy
- Stage 9.2.2 operational verification closure
- Stage 9.2.3 final source/runtime separation closure at
  `a5ce9b45c03a3d06098e29b3dec604caac1f4c73`

The controlling requirement is that secrets, database data, logs, backups,
temporary downloads, manifests, and original business files remain outside
Git. `/opt/aios-src` is source; `/opt/aios` is runtime. Structural separation
is primary. Ignore rules are defense-in-depth only.

## Authoritative category matrix

| Protected category | Approved structural location | Git/source rule |
|---|---|---|
| Production secrets and DSNs | `/opt/aios/runtime/config/runtime.env` or separately approved host secret facility | Never tracked or embedded in source, unit, tests, docs, commands, or logs |
| SSH private keys | Host SSH directories outside `/opt/aios-src`; never an AIOS runtime payload | Never tracked; public keys require intentional source authority |
| PostgreSQL persistent data | Active runtime bind mount under `/opt/aios/docker/postgres/data` | Never inside or tracked from `/opt/aios-src` |
| Database dumps/backups | Approved operator-controlled runtime backup location outside source | Never tracked; migration source SQL is not a dump |
| Logs | journald or a separately approved runtime log location | Never written into or tracked from source |
| Runtime cache | `/opt/aios/runtime/cache/pycache` and approved temporary facilities | Disposable; never tracked |
| Operational rollback | `/opt/aios/runtime/rollback/...` | Operational-only; never tracked |
| Original business files | `/opt/aios/data/documents/{images,voice,pdf,docs,links}` | Never tracked or copied into source |
| Document Manifests | `/opt/aios/data/documents/manifests` | Runtime/business metadata; never tracked |
| Temporary downloads | system temporary location isolated by `PrivateTmp=true`, then removed | Never retained or tracked in source |

The two repository files under `migrations/postgres/*.sql` are legitimate,
intentional schema migration source. They are not database dumps and must
remain trackable.
