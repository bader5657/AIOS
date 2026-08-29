# Production Authorization Provisioning and Runtime Prerequisites

## Exact future authorization artifact contract

No artifact is created by this package. A separately approved first-write stage
must exclusively provision this exact regular, non-symlink file:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/authorization.json`

Required metadata is owner `root`, group `aiosadmin`, mode `0440`, with every
path component real and non-symlink. Maximum file size is 16,384 bytes. The
content is strict UTF-8 JSON with duplicate keys rejected and exactly these
fields—no `issued_at` field exists in the implemented schema:

| Field | Exact contract |
|---|---|
| `schema_version` | `aios-stage-0.33c-candidate-create-authorization-v1` |
| `enabled` | JSON boolean `true` |
| `authorization_id` | canonical lowercase UUIDv4 |
| `not_before_utc` | canonical `YYYY-MM-DDTHH:MM:SSZ` |
| `expires_at_utc` | canonical `YYYY-MM-DDTHH:MM:SSZ`, later than `not_before_utc` |
| `max_requests` | JSON integer `1` |
| `operator_actor_reference` | `operator:<canonical-lowercase-UUIDv4>` |
| `source_manifest_reference` | exact approved retained canonical manifest path |
| `source_manifest_sha256` | lowercase 64-hex SHA-256 of that manifest's bytes |
| `trusted_facts_sha256` | lowercase 64-hex SHA-256 from the implemented canonical serializer |
| `evidence_session_id` | approved identifier matching `[a-z0-9][a-z0-9._-]{0,127}` |

The future governance authority must freeze the artifact's exact raw bytes and
SHA-256. The artifact is non-secret and must contain no credential, token,
environment value, unrestricted payload, or arbitrary path.

## Consumption infrastructure

No directory is provisioned here. A privileged operator prerequisite must
create the exact real, non-symlink directory:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/consumed`

Freeze its production metadata as `aiosadmin:aiosadmin`, mode `0700`. This is a
stricter exact choice within the implementation requirement that the directory
be owned by the executing effective UID/GID and have no group/world write bits.
It gives only the exact runtime identity create capability. Each marker is
`<authorization_id>.json`, created directly as `aiosadmin:aiosadmin`, mode
`0600`; no chmod/chown repair is permitted.

The runtime identity is established by `deploy/systemd/aios.service` and the
installed service metadata as Unix user/group `aiosadmin:aiosadmin`. A future
ephemeral invocation must execute as this exact identity. Privileged filesystem
provisioning requires separate Project Owner approval and operator execution.

## Database capability and secret readiness

The application identity remains
`aios_material_receipt_candidate_runtime`. Prior merged governance establishes
its governed membership in NOLOGIN writer role
`aios_material_receipt_candidate_writer`; no new role or `GRANT` is required or
authorized here.

`MaterialReceiptRepository.from_environment()` reads only
`AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD` and fixes host `127.0.0.1`, port
`5432`, database `aios`, and the candidate runtime username. The installed
service declares `/opt/aios/runtime/config/runtime.env`; bounded metadata shows
that file exists as a regular `root:aiosadmin` file, mode `0640`. Its content was
not read. Consequently the password's presence and validity are `UNKNOWN`, not
`AVAILABLE`. A future read-only, secret-safe preflight must prove variable
presence and connection readiness without disclosing the value; this package
does not modify `runtime.env` or contact production PostgreSQL.

## Controlled caller prerequisite

No permanent HTTP, CLI, Telegram, scheduler, worker, agent/tool, or Universal
Ingestion caller is registered. Repository search found no existing ephemeral
one-shot harness for `controlled_create_review_candidate`.

A separate first-write authority must therefore freeze and review an ephemeral
operator harness before use. It must run from the reviewed commit as
`aiosadmin:aiosadmin`, construct only the exact two DTOs from approved retained
evidence and facts, call `controlled_create_review_candidate` once, write the
bounded evidence contract, and exit. It must not be installed as a command,
service, handler, task, callback, or reusable production endpoint. No harness is
created here.

## Readiness classification

Dominant classification:
`D. RUNTIME_SECRET_OR_CALLER_PREREQUISITE_REQUIRED`.

Additional prerequisites also remain: privileged consumption-directory and
artifact provisioning, Project Owner-approved real input, retained evidence,
and a separately published first-write authority. These do not change the
dominant class because execution cannot be attempted until secret readiness and
the ephemeral caller are independently resolved.

## Frozen post-merge sequence and current gate

The complete sequence is seven distinct governed steps in exactly this order:

1. **Resolve runtime secret / caller prerequisites.**
2. **Govern and provision filesystem prerequisites.**
3. **Govern and build the ephemeral one-shot harness.**
4. **Select and approve real retained evidence and trusted business facts.**
5. **Publish a separate first-production-write authority.**
6. **Independently review and merge that first-write authority.**
7. **Execute exactly one bounded production write.**

Classification `D` means Step 1 is the current unresolved step. It does not
absorb or make optional Steps 2–7. No step may be collapsed, skipped, reordered,
or implicitly combined. Each step requires its own completion evidence and
governance boundary. If a step is incomplete or blocked, stop before advancing;
there is no implicit conditional authorization. After this PR merges, the next
official action is Step 1 only—not filesystem provisioning, harness creation,
input selection, authority publication, authority review, or execution.
