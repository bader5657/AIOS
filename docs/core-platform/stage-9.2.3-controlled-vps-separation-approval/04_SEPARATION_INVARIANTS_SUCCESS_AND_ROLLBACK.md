# Separation Verification, Invariants, Success, and Rollback

## Normal runtime and source-clean proof

Allow normal startup and module imports long enough to create meaningful cache
evidence. Do not manufacture business events or require a Telegram user
message.

After normal operation, prove:

- source HEAD is unchanged;
- tracked and staged diffs are empty;
- no untracked or ignored `__pycache__/` or `.pyc` exists in source;
- no other runtime residue appeared in source;
- bytecode exists beneath `/opt/aios/runtime/cache/pycache`;
- source-adjacent cache was not recreated; and
- runtime cache root remains `aiosadmin:aiosadmin 0750` and non-world-writable.

Source cleanliness after normal service execution is mandatory. Effective
unit configuration without this runtime proof is insufficient.

## Narrow operational invariants

- PostgreSQL: `aios-postgres` healthy, endpoint remains loopback-only at
  `127.0.0.1:5432`, connectivity unchanged, no migration or schema/data
  mutation.
- Storage: existing approved read/write capability remains operational; do not
  change modes, ownership, paths, or business data.
- Journald: startup visible, no crash/restart loop, bytecode permission error,
  Telegram conflict, or secret leakage.
- Service: active, enabled, exactly one poller, stable NRestarts.
- Reboot: `NONE`.

These are narrow non-regression checks only. They do not perform the full Stage
9.2.4 secrets/data/log/backup/business-file exclusion audit.

## Production success criteria

All are mandatory:

1. exact approved Stage 9.2.3 artifact installed;
2. exact runtime cache path and metadata;
3. active service and exactly one poller;
4. no predecessor/alternate poller;
5. exact cache-prefix environment active;
6. exact source read-only property active;
7. source clean after normal runtime imports;
8. bytecode present only in approved runtime cache;
9. PostgreSQL healthy and unchanged;
10. Storage operational and unchanged;
11. journald healthy with no secret leakage;
12. stable NRestarts;
13. predecessor unit and manifests preserved; and
14. no reboot.

Any failed mandatory criterion prevents a success claim and triggers stop or
rollback according to operational safety.

## Rollback

If the corrected service fails:

1. stop the corrected service;
2. prove zero pollers;
3. restore the exact preserved Stage 9.2.2 unit;
4. run `systemctl daemon-reload`;
5. start once; and
6. prove exactly one systemd-owned poller.

The runtime cache and quarantined bytecode may remain. Do not restore bytecode
to source. No source-code, runtime configuration, PostgreSQL/database, Docker,
Storage, or business-data rollback is authorized.
