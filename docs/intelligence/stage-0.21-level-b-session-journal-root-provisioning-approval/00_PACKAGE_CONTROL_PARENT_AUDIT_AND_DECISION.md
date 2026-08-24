# Stage 0.21 — Level B Session Journal Root Provisioning Approval

| Control | Authorized value |
|---|---|
| Work type | `OPERATIONAL GOVERNANCE ONLY` |
| Authority baseline | `1c71fc3bab508900f1ce055641c0d1c88f972257` |
| Harness validation | `PASS`; live provider inference `0` |
| Target | `/opt/aios/runtime/intelligence/staging/level-b-sessions` |
| Pre-activation target state | `ABSENT` |
| Owner / group | `aiosadmin:aiosadmin` |
| Mode | `0750` |
| Authorized mutation | create exactly one directory |
| Session/journal/inference | `NOT AUTHORIZED` |
| Decision | `APPROVED AFTER GOVERNANCE ACTIVATION` |

Read-only inspection at the authority baseline established that
`/opt/aios/runtime/intelligence/staging` resolves exactly to itself, is a real
directory rather than a symlink, and is owned by `aiosadmin:aiosadmin` with
mode `0755`. The target did not exist as a file, directory, or symlink.

The path chain was:

| Path | Owner / group | Mode | Type |
|---|---|---|---|
| `/opt` | `root:root` | `0755` | directory |
| `/opt/aios` | `aiosadmin:aiosadmin` | `0755` | directory |
| `/opt/aios/runtime` | `aiosadmin:aiosadmin` | `0775` | directory |
| `/opt/aios/runtime/intelligence` | `root:root` | `0755` | directory |
| `/opt/aios/runtime/intelligence/staging` | `aiosadmin:aiosadmin` | `0755` | directory |

The future operator identity is `uid=1000(aiosadmin)`,
`gid=1000(aiosadmin)`. It owns the immediate parent and can provision the
approved child without changing parent ownership or permissions. Mode `0750`
allows the owner to create, append, finalize, and review journals while
denying world access and group write.
