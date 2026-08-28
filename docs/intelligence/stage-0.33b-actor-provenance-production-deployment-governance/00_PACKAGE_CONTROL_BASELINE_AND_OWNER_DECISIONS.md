# Stage 0.33B Actor-Provenance Production Deployment Governance

Date: 2026-08-28 (Asia/Jakarta)

## Classification and non-execution boundary

This documentation-only package defines the production boundary for Migration
0005. It performs and authorizes no production connection, query, DDL, data or
privilege mutation, credential operation, service restart, or traffic
activation. Publication and merge are not preflight or execution authority.

Stage 0.32 is operationally verified and closed. Migration 0004 was deployed
once and must never be rerun. Stage 0.33A is merged and verified through PR
`#241`; its reviewed implementation commit is
`2a8c352dd41847ddf2dd48caac4643d4f31e8808` and its merge/main baseline is
`466509f9b4c0fb6fcd3f47956443842f4da4eb3b`.

| Control | Frozen value |
|---|---|
| UP path | `migrations/postgres/0005_add_material_receipt_creator_provenance.up.sql` |
| UP SHA-256 | `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293` |
| DOWN path | `migrations/postgres/0005_add_material_receipt_creator_provenance.down.sql` |
| DOWN SHA-256 | `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` |
| Container / image | `aios-postgres` / PostgreSQL `17.x` (`postgres:17-alpine`) |
| Database / administrative role | `aios` / `aios` |
| Schema / target | `public` / `public.material_receipts` |

Any source, path, hash, target, identity, or schema mismatch blocks later
authority. The only eligible administrative transport is the established fixed
argv shape:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

SQL is supplied through stdin from an exact reviewed artifact or verifier.
Credentials, DSNs, environment values, and connection strings must not appear
in argv, logs, or evidence. Host `psql`, host sockets, external endpoints,
arbitrary containers/databases/roles, and production fallback are prohibited.

## Exact permitted effect

The future one-shot transaction may produce only:

1. `public.material_receipts.created_by_actor_reference TEXT NOT NULL`;
2. named CHECK `material_receipts_created_by_actor_reference_valid`, enforcing
   `operator:<canonical lowercase RFC4122 UUIDv4>`; and
3. `INSERT (created_by_actor_reference)` for
   `aios_material_receipt_candidate_writer`.

It may add no default, backfill, nullable phase, index, trigger, function,
table, timestamp, owner, role, membership, ADMIN OPTION, posting privilege,
stock/movement privilege, or unrelated ACL. Migration 0004 and
`material_receipts_source_asset_active_uidx` are immutable.

## Authority sequence

Every Stage 0.33B control uses this one canonical sequence, without omission or
shortcut:

1. **0.33B-G** — governance review and merge;
2. **0.33B-P** — separately authorized production READ-ONLY preflight;
3. **0.33B-A** — separately reviewed and merged one-shot Migration 0005
   execution authorization, bound to fresh passing preflight evidence, current
   clean main, and the frozen UP hash;
4. **0.33B-D** — exactly one controlled production Migration 0005 execution
   attempt under active 0.33B-A; and
5. **0.33B-V** — separately authorized new-session READ-ONLY post-deployment
   verification.

The execution attempt need not be fragmented into another documentation PR
after 0.33B-A is reviewed and merged; it is the controlled consumption of that
authority. Preflight cannot be combined with DDL authority because its result,
especially the zero-row gate, is an input to independent one-shot approval.
Post-deployment verification remains separate so it observes committed state
from a new session.

## Project Owner decisions

The Project Owner approves this safe design and records all of the following:

1. production Migration 0005 requires exactly zero `material_receipts` rows;
2. any existing row is a hard stop requiring historical-provenance governance;
3. historical provenance must never be fabricated;
4. preflight authority is separate and read-only;
5. Migration 0005 requires separately reviewed one-shot execution authority;
6. only the exact committed, immediately hash-verified UP artifact may run;
7. execution has one attempt and no automatic retry;
8. production DOWN is not authorized;
9. every pre-COMMIT failure rolls back and stops;
10. post-deployment verification is separate and read-only;
11. the actor-provenance gate closes only after that verification passes; and
12. candidate activation remains unauthorized until the runtime-secret and
    explicit production safety-review gates separately close.

These decisions approve governance architecture only. They are not production
preflight, DDL, DOWN, repair, retry, credential, restart, or activation
authority.
