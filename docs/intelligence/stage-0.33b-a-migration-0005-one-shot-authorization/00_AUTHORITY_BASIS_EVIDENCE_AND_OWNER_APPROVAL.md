# Stage 0.33B-A Authority Basis, Evidence, and Owner Approval

Date: 2026-08-28 (Asia/Jakarta)

## Publication boundary and inactive authority

This package is authorization documentation only. Publication does not contact
production PostgreSQL, execute a SELECT, run Migration 0005 or Migration 0004,
perform DDL, DML, or a lock, change ownership/roles/grants/memberships, modify
`runtime.env`, restart PostgreSQL/Docker/`aios.service`, change Telegram or
Universal Ingestion, activate candidate traffic, or perform Stage 0.33B-V.

This package proposes exactly one future controlled production execution attempt
of Migration 0005 UP. Publication alone grants no active execution authority.
Authority activates only after independent Stage 0.33B-A review PASS with zero
blockers, merge unchanged, continuing Project Owner approval, and every immediate
activation gate in this package passing. The authority is transactional,
fail-closed, one-shot, and permits no retry, DOWN, repair, or runtime activation.

The one-shot Migration 0005 authority is permanently consumed at the first
attempt to launch the exact governed production control-plane process, not when
`BEGIN;` is submitted. A Docker failure, failure to start `psql`, rejected
connection, stdin failure, connection loss before `BEGIN;`, or failed `BEGIN;`
still consumes it. No production PostgreSQL connection test, `SELECT 1`, test
connection, manual or alternate Docker/`psql` launch, credential-bearing DSN
probe, or alternate `pg_isready` connection session may precede that launch.
Non-database container and process metadata remain eligible only within the
bounded activation gates.

The Stage 0.33B-D evidence root is already provisioned persistent governed
infrastructure. Its governing dependency is Stage 0.33B-FP PR `#250`, merged and
verified at merge commit `677640c269dad3101c6156a425f5f46ee3d1dd56`. Under
that governance, the authenticated human operator provisioned the root and
Codex independently completed the bounded post-provision verification with
PASS. PR `#250`'s privileged operator provisioning authority is historical and
must not be incorporated into this Migration execution authority.

The verified chain is `/opt/aios/runtime/intelligence`, a real non-symlink
directory owned by `root:root`, mode `0755`;
`/opt/aios/runtime/intelligence/production-execution-evidence`, a real
non-symlink directory owned by `root:root`, mode `0755`; and
`/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d`, a
real non-symlink directory owned by `aiosadmin:aiosadmin`, mode `0750`.
Stage 0.33B-FP also verified a single exclusive mode-`0600`
`aiosadmin:aiosadmin` probe with the exact bounded content, flush, fsync, exact
cleanup, and absence afterward all PASS. No repeat provisioning probe is
required or authorized by this remediation.

Immediately before any evidence session is initialized, Stage 0.33B-D must
non-mutatingly verify with `lstat`/`stat` that the intermediate and Stage roots
retain those exact type, non-symlink, owner/group, and mode properties. Any
absence, symlink, wrong type, owner, group, or mode classifies `STAGE 0.33B-D
ACTIVATION BLOCKED — VERIFIED EVIDENCE ROOT DRIFT`: do not repair, execute
`sudo`, or contact PostgreSQL, and leave Migration authority UNCONSUMED.
Stage 0.33B-D has no sudo or root-filesystem-mutation authority; it may perform
only non-privileged `aiosadmin` operations beneath the verified Stage root.

Each exclusively created non-privileged session uses
`stage-0.33b-d-migration-0005-YYYYMMDDTHHMMSSffffffZ-<canonical-lowercase-UUIDv4>`,
is mode `0750`, and exclusively creates only `execution.jsonl` (`0640` while
executing) and final `manifest.json`. UTF-8 JSONL records are bounded, sanitized,
flushed and fsynced at critical phases; finalization includes a prohibited-secret
scan, JSONL SHA/size/count, an exclusively created bounded manifest, file and
directory fsync, final file modes `0440`, and a SHA-256 of the complete final
manifest bytes reported externally. Existing paths/files are hard stops; no
overwrite, root deletion, symlink following, or broad filesystem authority
exists. The persistent Stage root is never deleted after any terminal outcome;
each future separately authorized attempt uses a new session directory. Root
verification or session initialization does not consume Migration authority.
Any pre-launch evidence failure leaves authority UNCONSUMED; any post-launch
evidence failure leaves it CONSUMED and requires fail-closed rollback if still
pre-COMMIT, with no retry. Stage 0.33B-V remains separate.

## Repository and reviewed-evidence basis

Publication was originally based on clean synchronized main at
`a6facdfb573d4dce406d0541b7317ffb9d235f9e`, the merge of evidence PR `#248`.
This provisioned-root remediation is synchronized onto current main
`677640c269dad3101c6156a425f5f46ee3d1dd56`, the merge of Stage 0.33B-FP PR
`#250`. PR `#248`'s reviewed head was
`35c75da03b519efdc523b4c1adc0d6d9047c1846`. The controlling reviewed package is:

`docs/intelligence/stage-0.33b-p-preflight-execution-evidence/`

Stage 0.33B-P classified PASS. Stage 0.33B-PE classified FINAL ORIGINAL
EXECUTION EVIDENCE REVIEW PASS and evidence quality A: ORIGINAL EXECUTION
EVIDENCE — SUFFICIENT. No production preflight rerun is required. PR `#244`, PR
`#245`, and PR `#247` authorities are independently and permanently consumed.
They are not revived or reusable.

## Immutable original-evidence binding

| Evidence unit | Reviewed SHA-256 |
|---|---|
| Original Codex JSONL | `0d2ebc28adcdb8b4bab16ec65f9e1fd7627ef3cf5a93ba94d8d1a57fc4a16354` |
| Bounded relevant record set | `7143a431691c0fcf8371abd8dbdfc840d92bbe1e1c16a88369bd7dcbf3663dc4` |
| Execution stdout | `73c83cd8e22af2b22a6eac2636f06cf003ee00d845c32c0b4f7687bf5fe5b203` |
| Canonical preflight SQL bundle | `64435ab0193ceb454569496f954a9c6788355f035834d7a6b095222b5154d6f3` |
| Retained SQL transport | `0e196fc188498bc6b74dc191b33f8b74bbfe96d1ae7f7280c72d93c7fb82dafa` |
| Execution-result manifest | `c0bb9341fdbe489a78661fef3bc54308202281e14bf93c9bc09465ba3a008d04` |

The original execution identities are Codex thread/session
`01a04816-112d-7231-b987-fca86b496e91`, successful execution turn
`01a0485a-88ab-76b3-94ff-60f4857ce1bc`, production process session `56195`, and
execution command `exec-27088f48-d769-4a8e-ac40-5ea1bec27a23`. The raw JSONL is
not copied into this repository. This authorization relies on the merged,
independently reviewed evidence package—not a screenshot, conversation summary,
or reconstructed baseline.

## Frozen verified target and prestate

| Field | Reviewed production value |
|---|---|
| Container / image | `aios-postgres` / `postgres:17-alpine` |
| PostgreSQL | `17.10` |
| Database / owner / session user | `aios` / `aios` / `aios` |
| Schema / owner | `public` / `pg_database_owner` |
| Relation / kind / owner | `public.material_receipts` / `r` / `aios` |

The frozen control plane is `/usr/bin/docker exec -i aios-postgres
/usr/local/bin/psql -X -v ON_ERROR_STOP=1 -U aios -d aios`, with governed SQL
and the exact migration artifact supplied through stdin. Alternate container,
database, user, endpoint, client, argv substitution, or fallback is prohibited.
The first attempt to launch precisely this argv consumes the one-shot authority.

The reviewed preflight proved creator column
`created_by_actor_reference` ABSENT and named CHECK
`material_receipts_created_by_actor_reference_valid` ABSENT. Migration 0005 was
not executed. These are historical reviewed facts, not an assumption that the
state remains current; deployment must recheck them under lock before DDL.

The Stage 0.32 index `material_receipts_source_asset_active_uidx` was present,
valid, ready, unique, sole-keyed by `source_asset_reference`, with the approved
active-source predicate excluding `REJECTED` and `CANCELLED`. Migration 0004
must not rerun.

## Frozen preservation baseline

| Table | Row count | Row digest |
|---|---:|---|
| `public.material_receipts` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.material_receipt_items` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.inventory_movements` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `public.material_stock` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |

The reviewed structural/security baseline contains 47 bounded column rows, 42
constraint rows, 12 index rows, four governed tables owned by `aios`, captured
ACLs, no non-internal governed-table triggers or associated functions, six
frozen roles, two governed runtime-to-writer memberships with ADMIN OPTION false
for both, 36 table-privilege rows, and 335 column-privilege rows. Deployment
must compare against the stronger structured evidence in PR #248, not counts
alone, and must freshly recheck every fingerprint after all four frozen locks are
held. The immutable lock order is `material_receipts` ACCESS EXCLUSIVE,
`material_receipt_items` SHARE, `inventory_movements` SHARE, then
`material_stock` SHARE, all under the same transaction-local five-second lock
timeout. The same locks remain held through the post-DDL fingerprint comparison
and COMMIT or ROLLBACK.

## Project Owner approval

The Project Owner approves exactly one future controlled Migration 0005 UP
production execution attempt, only after this authorization receives independent
review PASS, is merged unchanged, and all activation gates pass.

The Owner does not authorize Migration 0004, Migration 0005 DOWN, retry, a
second attempt, historical backfill, ownership repair, unrelated grants, role or
membership changes beyond the exact Migration 0005 grant delta, candidate
activation, service restart, Telegram change, or Universal Ingestion change.

