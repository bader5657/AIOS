# Runtime Config Parent Directory Security Boundary Evaluation

Date: 2026-08-25 (Asia/Jakarta)

## Verified baseline

The writer bootstrap helper remains unimplemented. No credential, writer role,
database change, `runtime.env` change, service restart, Docker change, Telegram
change, or business-data mutation occurred.

The production path is on the root ext4 filesystem (`/dev/sda1`, read-write).
Metadata is:

| Path | Owner | Group | Mode | Type |
|---|---|---|---:|---|
| `/opt` | root | root | `0755` | directory |
| `/opt/aios` | aiosadmin | aiosadmin | `0755` | directory |
| `/opt/aios/runtime` | aiosadmin | aiosadmin | `0775` | directory |
| `/opt/aios/runtime/config` | aiosadmin | aiosadmin | `0775` | directory |
| `/opt/aios/runtime/config/runtime.env` | root | aiosadmin | `0640` | regular file |

`config` contains only `runtime.env`. No symlink or special file was observed.
No extended ACL marker was present; `getfacl` is unavailable. `lsattr` reported
only the normal extents flag (`e`), with no immutable/append-only attribute.

## Security finding

POSIX removal and rename authorization is controlled by the parent directory.
The current `aiosadmin` identity has write and execute access to `config`, so it
can create sibling entries and replace/remove the `runtime.env` directory entry
without writing the existing root-owned inode.

Changing only `config` is also insufficient: `aiosadmin` can replace the
`config` directory entry through writable `/opt/aios/runtime`, and can replace
`runtime` through owner-writable `/opt/aios`. The root-mediated-only boundary is
therefore currently invalid along the whole path below `/opt`.
