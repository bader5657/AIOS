# Stage 0.33C-P1ER Evidence Root Identity, Mode, and Scope

## Scope and source gate

This package governs only the Step 1 runtime-sync evidence root. It does not
provision filesystem, synchronize `/opt/aios-src`, restart services, contact
PostgreSQL, begin Step 2, create an authorization artifact or consumed
directory, build a harness, create first-write authority, or activate traffic.

The publication source gate is `HEAD == main == origin/main ==
9d7d5dc7e273d0d939dda3dae93c97211aa13cb4`, with a clean worktree. PR #267 is
MERGED / VERIFIED; its sync authority is MERGED / CONDITIONAL, consumed `0`,
and runtime synchronization has not executed. Step 1 is OPEN and Step 2 is
NOT AUTHORIZED.

## Exact evidence root

The only accepted root is:

`/opt/aios/runtime/intelligence/production-candidate-create/stage-0.33c/runtime-sync-evidence/`

It is exclusively for bounded Stage 0.33C-P1 runtime source-synchronization
evidence. It is not the Step 2 authorization parent, consumed directory, or
candidate-write evidence filesystem. No caller-selected or environment-
controlled alternate path is permitted.

## Read-only parent audit

| Path | Type / symlink | Owner/group | Mode | State |
|---|---|---|---|---|
| `/opt/aios` | real directory, non-symlink | `root:aiosadmin` | `0755` | exists |
| `/opt/aios/runtime` | real directory, non-symlink | `root:aiosadmin` | `0755` | exists |
| `/opt/aios/runtime/intelligence` | real directory, non-symlink | `root:root` | `0755` | exists |
| `.../production-candidate-create` | absent | — | — | not provisioned |
| `.../stage-0.33c` | absent | — | — | not provisioned |
| `.../runtime-sync-evidence` | absent | — | — | not provisioned |

The absent state is expected and safe. No path was created or repaired by this
publication.

## Three-governance provenance chain

All future provisioning and runtime-sync evidence must carry the complete,
ordered governance chain:

1. PR #266 — Runtime Source / Import Synchronization Governance;
2. PR #267 — Runtime Sync One-Shot Execution Authority; and
3. PR #268 — Runtime Sync Evidence-Root Provisioning Governance.

Before this PR merges, its provenance is identified as PR #268, reviewed HEAD
`7100e4ee4d65cae0d71362032659a981578b7fa6`, state `UNMERGED / REVIEWED`. No
future merge SHA is guessed or placed in evidence. After merge, the exact PR #268
merge commit must be captured and verified before provisioning or sync authority
activation; if it cannot be established, STOP.

## Frozen root contract

After separate approval and privileged provisioning, the evidence root itself
must be a real non-symlink directory owned `aiosadmin:aiosadmin`, mode `0750`.
The mode permits the runtime executor to create governed child sessions while
preventing world access and uncontrolled group write. Existing-path behavior is
strict: absent may be provisioned; exact matching metadata may be reused; any
wrong type, symlink, owner, group, or mode is STOP. No chmod, chown, delete,
recreate, or automatic repair is permitted.

## Session and file model

Execution never writes directly into the shared root. Each attempt receives one
session directory named
`stage-0.33c-p1s-runtime-sync-<UTC_TIMESTAMP>-<canonical-lowercase-UUIDv4>`.
The session is exclusively created as a real non-symlink directory owned
`aiosadmin:aiosadmin`, mode `0750`; no reuse or overwrite is allowed. A session
collision is STOP, with no deletion or fallback identity generation.

Exactly two files are required inside the session: `execution.jsonl` and
`manifest.json`. Both are created exclusively mode `0600`, owned
`aiosadmin:aiosadmin`, and finalized mode `0440` after durable completion. No
arbitrary logs, stdout dumps, environment dumps, or source-file copies are
allowed.
