# Controlled Execution, Validation, and Project Owner Decision

## Future bounded execution

This evaluation authorizes no filesystem mutation. A separate one-attempt
authority must bind exactly to ownership/mode changes on:

1. `/opt/aios` -> `root:aiosadmin 0755`;
2. `/opt/aios/runtime` -> `root:aiosadmin 0755`;
3. `/opt/aios/runtime/config` -> `root:aiosadmin 0750`.

Before change, capture path/inode/filesystem metadata, `runtime.env` metadata and
bounded content fingerprint, service health, and config read capability. After
change, prove exact metadata, unchanged file fingerprint, unchanged service
health, successful read/traverse as the service identity, inability of
`aiosadmin` to create/remove/rename config entries, and root same-filesystem
atomic-replacement capability using only a disposable non-secret probe artifact.
Do not replace `runtime.env` during validation.

No ACL, sticky bit, sudoers, helper, secret, database role, Docker, application,
Telegram, or data change is part of that execution.

## Project Owner decision

Approve the three-directory ancestor-chain hardening above, root-only write
authority, group read/traverse compatibility, no separate secret directory, no
ACL, no sticky bit, live application without restart, and metadata-only rollback
posture.

Writer bootstrap helper implementation remains blocked until this governance PR
merges, the separately authorized filesystem hardening succeeds, and post-change
validation proves the complete path boundary. Only then may repository helper
implementation receive fresh authority.
