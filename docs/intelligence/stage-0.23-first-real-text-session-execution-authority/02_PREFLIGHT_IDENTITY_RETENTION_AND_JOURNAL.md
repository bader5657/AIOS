# Preflight, Identity, Retention, and Journal Contract

## Mandatory fresh preflight

Reuse the complete Stage 0.21 preflight before session creation:

- clean synchronized source and exact runtime/config identity;
- authoritative interpreter and dependency identity;
- repository module identity;
- network isolation and accepted privileged-network evidence identity/hash;
- fresh lightweight network-drift checks, with no new sudo in the harness;
- AIOS active/running with frozen `MainPID` and `NRestarts=0`;
- healthy PostgreSQL without querying business data;
- exactly one Telegram poller, without using Telegram as ingress;
- safe RAM, swap, load, and disk;
- healthy staging container;
- no restart or OOM evidence.

Additionally verify the Stage 0.22 eligibility module identity, `real_text`
data class, exact candidate authority, no-raw retention policy, and corrected
independent counter taxonomy.

The authoritative interpreter is `/opt/aios/runtime/venv/bin/python` and must
identify as Python `3.12.3` with httpx `0.28.1`. Use process-local `sys.path`
binding only, rooted at `/home/aiosadmin/AIOS`.

Before session creation, all of these modules must resolve beneath that
repository root:

- `core.ingestion.real_data_eligibility`
- `core.core_to_brain_mapper`
- `core.brain.schema_binding`
- `core.brain.staging_composition`

Any preflight or identity mismatch is fail-closed. PostgreSQL health is a
service safety check only and does not authorize a query.

## Input evidence and retention

The runtime journal must not persist the raw candidate. It may retain:

| Evidence | Authorized value |
|---|---|
| SHA-256 | `2ab0a632dfd5b08e344a87bdcf9922b87cc27cbe1052df63e57c5e1958a772c5` |
| Unicode code-point count | `27` |
| UTF-8 byte count | `27` |
| Data class | `real_text` |
| Eligibility evidence | classification and reason code only |

The exact candidate is present in this governance package solely because the
Project Owner supplied it for explicit authorization. It must not be copied to
runtime/session evidence.

Raw model output is displayed to the operator only. The journal must not retain
raw output or an output hash. It may retain success/failure metadata, output
size when required, schema result, provider/model identity, and latency.

## Journal lifecycle

The future execution must exclusive-create one new unique Session-Bound Level B
journal with `data_class=real_text`. It is append-only, contains no raw input or
raw output, and is finalized exactly once with a journal SHA-256. No journal is
created by this publication task.
