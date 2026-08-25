# Permission, Service, and Compatibility Evidence

## Write boundary

The ordinary `aiosadmin` identity has group access along the protected chain.
Modes `0755`, `0755`, and `0750` provide traverse but no group write bit. Under
POSIX directory authorization, creating or removing an entry, renaming an entry
from or into a directory, and replacing a target by rename require write and
execute permission on the affected parent directory. Consequently ordinary
`aiosadmin` cannot create, remove, or rename entries in `config` and cannot
replace `runtime.env` through directory-entry manipulation.

The same absence of non-root write permission on `/opt/aios` and
`/opt/aios/runtime` prevents replacement of either protected descendant
directory through its parent. The root-mediated replacement boundary is valid
across the complete chain. No destructive target probe was performed; the
Project Owner's reported negative probes left no artifacts.

## Service postflight and read compatibility

Read-only systemd inspection observed:

| Property | Result |
|---|---|
| Unit | `aios.service` |
| Active state | `active` |
| Substate | `running` |
| Linux user/group | `aiosadmin:aiosadmin` |
| MainPID | `15845` |
| Restart count | `0` |
| Unit result / main status | `success` / `0` |

No restart was performed. The service remained active/running after hardening,
with no restart, which establishes no hardening-induced service failure.

The observed path modes give the service identity traverse access through
`/opt/aios`, `/opt/aios/runtime`, and `/opt/aios/runtime/config`, and group-read
access to the regular `runtime.env`. Successful digest calculation as ordinary
`aiosadmin` independently exercised access to the complete file without
printing its contents. Runtime read compatibility therefore passes.

## Root replacement compatibility

`config` is a root-owned directory on the same mounted filesystem as its
`runtime.env` child, and root retains directory `rwx`. Structurally, root can
create an exclusive unpredictable temporary file inside `config`, restrict and
validate it, write and `fsync` it, set final metadata, atomically rename it over
the target within that directory, and `fsync` the parent. This conclusion needs
no replacement of `runtime.env` and no secret generation. Root atomic
replacement compatibility passes.
