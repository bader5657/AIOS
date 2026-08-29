# Synchronization, Rollback, and Service Boundary

## Exact future synchronization contract

No synchronization is executed by this package. After separate approval, an
operator may use the repository-standard equivalent of this pinned sequence:

1. fetch the expected `origin` repository and verify the exact target commit
   object `964193f2e567b5109de50c427bbbf632b2198958`;
2. recheck `/opt/aios-src` has no local modifications, unknown commits, or
   untracked runtime artifacts;
3. record the pre-sync rollback identity
   `2c44dc84cb38dc51778f8a65f12a6e59683c74c9`;
4. move the checkout, without manual file edits, to detached exact target
   `964193f2e567b5109de50c427bbbf632b2198958`; and
5. run the separately frozen post-sync import, commit, and cleanliness checks.

The method must be commit-pinned (for example, fetch followed by checkout of
the exact SHA), never an unpinned `git pull` or moving-branch merge. Manual copy,
partial `rsync`, unreviewed cherry-pick, and force-reset are prohibited. If any
pre-sync drift appears, STOP and return to governance.

Rollback means returning the source checkout to the recorded exact commit
`2c44dc84cb38dc51778f8a65f12a6e59683c74c9`, subject to a fresh operator decision.
It does not delete evidence or alter database/schema state.

## Service relation and restart boundary

Installed `aios.service` metadata is `User=aiosadmin`, `Group=aiosadmin`,
`WorkingDirectory=/opt/aios-src`, and
`ExecStart=/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`.
The service is active with its existing PID/start identity. Python imports module
code into the running process at process start; changing an on-disk checkout
does not change resident code.

The Stage 0.33C callable is dormant and not part of the active Telegram service
entrypoint. Therefore source synchronization alone does not require restarting
`aios.service`. No restart authority is granted here. If a future implementation
or health check proves a restart technically necessary, classify
`SEPARATE_RESTART_AUTHORITY_REQUIRED` and stop; do not restart automatically.

No service, runtime environment, credential, filesystem, database, Telegram, or
Universal Ingestion mutation is authorized by this governance.
