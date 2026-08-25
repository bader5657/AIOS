# Root Helper, Locking, Atomic Replacement, and Preservation

## Execution model

An operator manually authenticates `sudo` once to execute a fixed, reviewed,
single-purpose bootstrap. The temporary helper is installed/executed as root,
owned by root, mode `0700`, not writable by `aiosadmin`, and removed after the
session. It has fixed file paths, environment keys, database/container target,
and role/login names. It accepts no arbitrary command, key, target, output path,
or secret value. No persistent sudoers entry is permitted.

## File algorithm

The root process must:

1. disable shell tracing and restrictive umask `077`;
2. open a root-owned exclusive lock file on the same config filesystem;
3. open and validate the existing regular, non-symlink `runtime.env` by file
   descriptor, owner, group, mode, and path containment;
4. reject either approved key if already present unless a separately governed
   reconciliation explicitly authorizes replacement;
5. generate both secrets in process memory;
6. construct a byte-preserving replacement, retaining every unrelated line in
   its original order and bytes and appending exactly the two new assignments
   before one final newline;
7. create a same-directory unpredictable temporary file using exclusive-create
   semantics, owner `root`, mode `0600`, never `/tmp`;
8. write completely, validate key uniqueness/presence without displaying
   values, `fsync` the file, set final owner `root:aiosadmin` and mode `0640`;
9. atomically rename it over `runtime.env`, then `fsync` the parent directory;
10. retain the original bytes only in process memory/open file state until DB
    provisioning and authentication succeed.

No incremental append/edit is allowed. Necessary addition of the two new lines
and preservation of the existing final newline are the only formatting changes.

## Backup and cleanup

No persistent plaintext backup is retained. For same-session rollback, the root
process holds the original bytes privately and can reconstruct a root-owned
mode-`0600` same-directory rollback temporary, atomically restore it, and fsync
the directory. All temporary names, open descriptors, and in-memory buffers are
released on success/failure; helper and lock artifacts are removed when safe.
Crash recovery treats persisted keys with absent/disabled matching logins as an
ambiguous incomplete bootstrap and stops for governance—never silently reuses
them.
