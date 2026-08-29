# Stage 0.33B-V-FP Post-Provision Verification and Handoff

Date: 2026-08-29 (Asia/Jakarta)

## Bounded non-mutating path verification

After future human execution, Codex may verify without sudo that:

- `/opt/aios/runtime/intelligence/production-execution-evidence` is a real,
  non-symlink directory owned by `root:root` with mode `0755`; and
- `/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v`
  is a real, non-symlink directory owned by `aiosadmin:aiosadmin` with mode
  `0750`.

Path verification must use bounded filesystem metadata only. It must not read
Stage D evidence content or use sudo. Any mismatch stops verification without
repair.

## Single write/fsync probe

Only after path verification passes, exactly one non-privileged probe attempt
as `aiosadmin` is authorized. Generate exactly one canonical lowercase UUIDv4
and bind the sole probe path as:

```text
/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v/.provisionability-probe-<canonical-lowercase-UUIDv4>
```

Create that exact file exclusively with no overwrite and mode `0600`, owned by
`aiosadmin:aiosadmin`. Its exact contents, with no additional bytes, are:

```text
AIOS_STAGE_0_33B_V_EVIDENCE_ROOT_PROBE
```

Write, flush, and fsync the file; verify exact content, regular-file type,
non-symlink status, owner/group, and mode; delete only that exact generated
probe; then verify it is absent. No sudo is authorized.

If the generated path already exists, stop: do not overwrite or delete it and
do not generate another name in the same attempt. Any create, write, flush,
fsync, metadata, content, deletion, or absence-verification failure produces:

```text
STAGE 0.33B-V EVIDENCE-ROOT PROVISIONING VERIFICATION BLOCKED
```

On failure, do not contact PostgreSQL, do not repair automatically, and do not
claim provisioning PASS. Stage 0.33B-V authority remains unconsumed.

## Evidence and secret safety

Verification records may retain only bounded path, type, symlink, owner/group,
mode, probe UUID/path, lifecycle outcome, and timestamps. They must not retain
sudo or terminal password input, environment dumps, `runtime.env` contents,
`DATABASE_URL`, database credentials, tokens, API keys, private keys, raw
business rows, or Stage D evidence content.

## Persistence and execution handoff

After successful provisioning verification, the Stage V root becomes
persistent governed AIOS infrastructure. Do not delete it after one
verification session or revert its ownership/mode. Future separately authorized
verification sessions may create unique session directories beneath it.

Provisioning PASS does not execute or activate Stage 0.33B-V. Before a separate
execution, reverify that PR #254 remains authoritative, source/main are
synchronized, the exact query-bundle SHA-256 remains
`304fdf5fbf63bcea9c8e41ddb8e921831a9b4a01a1262acca2cfd09273e855f1`, the
Stage V root still satisfies this contract, semantic evidence files can be
created, and every PR #254 activation gate passes. Production candidate
activation remains not authorized.
