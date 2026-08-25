# Exact Invariant, Change Risk, and Rollback

## Approved target invariant

| Path | Owner | Group | Mode | Writers | Readers/traversers |
|---|---|---|---:|---|---|
| `/opt/aios` | root | aiosadmin | `0755` | root | root, aiosadmin group, others |
| `/opt/aios/runtime` | root | aiosadmin | `0755` | root | root, aiosadmin group, others |
| `/opt/aios/runtime/config` | root | aiosadmin | `0750` | root | root and aiosadmin group |
| `runtime.env` | root | aiosadmin | `0640` | root | root and aiosadmin group |

Only root may create, remove, or rename directory entries at each protected
boundary. Authorized `aiosadmin` readers retain traverse/read capability.
Existing child directories keep their own ownership/modes, so the application
continues writing cache/runtime data where already authorized.

A root helper remains able to lock, create a same-directory mode-`0600`
temporary file, fsync, set `root:aiosadmin 0640`, atomically replace
`runtime.env`, and fsync `config`.

## Change risk

The active service does not need parent-directory write access. Changing
directory metadata is live and does not invalidate open file descriptors or the
already-loaded environment. No service restart is required. A future service
restart remains compatible because root/systemd and `aiosadmin` retain path
traversal and file read access.

Operational tooling will no longer be able to create, delete, or rename
top-level children directly under `/opt/aios` or `/opt/aios/runtime` without
root mediation. Existing writable child directories remain usable. Future
top-level layout changes must be explicitly root-mediated, which is the intended
security posture.

## Rollback posture

Rollback is metadata-only and separately controlled: restore the observed
owners/modes (`/opt/aios` `aiosadmin:aiosadmin 0755`; `runtime` and `config`
`aiosadmin:aiosadmin 0775`) only if compatibility validation fails. Rollback
must not alter `runtime.env` content or its `root:aiosadmin 0640` metadata.
