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

Provisioning and verification records may retain only bounded, sanitized
filesystem facts: governed path identifier, file type, symlink state, owner,
group, mode, whether the exact command was required, bounded command result
status, safe exit/result code, probe identity, probe `PASS`/`BLOCKED`, final
provisioning classification, and timestamps. Raw unrestricted stdout or stderr
capture, arbitrary terminal text, and full shell/session transcripts are
prohibited.

Records must not retain a sudo password, password-prompt response, terminal
password input, environment contents or environment-variable dumps,
`runtime.env` contents, `DATABASE_URL`, database passwords,
credential-bearing DSNs or diagnostics, tokens or bot tokens, API keys, private
keys, SSH private keys or other `PRIVATE KEY` material, raw business rows,
unrestricted command stdout, unrestricted command stderr, sudo conversation,
or Stage D evidence content. If an error message may contain secret material,
do not copy it verbatim. Retain only bounded non-secret fields such as operation
ID, failure class, safe exit/result code, and governed path identifier.

The existing human password boundary remains unchanged: a human enters any
sudo password directly in the VPS terminal. Codex must never request, receive,
capture, log, store, or pipe it. `sudo -S`, `expect`, password automation,
sudoers modification, and passwordless sudo remain prohibited.

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

## Authoritative post-merge operator sequence

After PR #255 receives independent review PASS, the required sequence is:

1. Merge PR #255 unchanged.
2. Synchronize repository `main` and verify it is clean.
3. **CODEX MUST STOP.** The review/merge task must not execute sudo,
   `/usr/bin/install`, filesystem provisioning, the probe, or Stage V
   PostgreSQL execution.
4. In a separate human operation, an authenticated Project Owner or explicitly
   authorized VPS operator opens and authenticates to the VPS terminal and
   verifies the frozen parent state.
5. If the Stage V root is absent, the human operator—and only the human
   operator—executes exactly:

   ```text
   /usr/bin/sudo /usr/bin/install \
     -d \
     -o aiosadmin \
     -g aiosadmin \
     -m 0750 \
     /opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-v
   ```

6. The human operator reports completion only. Codex may display or restate the
   already-approved command but must not execute it.
7. Codex resumes in a separate task and performs only bounded, non-privileged
   metadata verification.
8. Only if metadata verification passes, Codex performs exactly one governed,
   non-privileged write/fsync probe.
9. Classify provisioning verification as `PASS` or `BLOCKED`.
10. Only after provisioning PASS may a separately governed Stage 0.33B-V
    execution task evaluate its remaining activation gates.

A single Codex task must not combine review, merge, sudo provisioning, probe,
and Stage V execution. The required boundaries are: review/merge task ≠ human
provisioning ≠ Codex verification/probe task ≠ Stage V production read-only
execution task. Provisioning, verification, and the probe do not consume Stage
V authority; consumption remains only the first attempt to launch PR #254's
exact production Docker/psql control plane.
