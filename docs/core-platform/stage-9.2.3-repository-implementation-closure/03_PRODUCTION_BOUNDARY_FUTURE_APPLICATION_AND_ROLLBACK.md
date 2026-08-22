# Production Boundary, Future Application, and Rollback

## Current production boundary

At repository closure:

- the corrected repository artifact exists;
- it is not yet installed on the VPS;
- `/opt/aios/runtime/cache/pycache` has not yet been created for Stage 9.2.3;
- production continues to use the installed Stage 9.2.2 unit;
- no Stage 9.2.3 service restart or daemon reload has occurred;
- no Stage 9.2.3 source/runtime operational verification has occurred; and
- no VPS mutation occurs in this governance workflow.

Therefore this closure does not claim production separation complete.

## Exact future controlled VPS application scope

A separate production approval may authorize only this sequence:

1. authenticate to `aios-prod-01`;
2. verify the current healthy exactly-one-poller state;
3. create `/opt/aios/runtime/cache/pycache`;
4. set owner/group `aiosadmin:aiosadmin`;
5. set directory mode `0750`;
6. preserve the installed Stage 9.2.2 unit as rollback evidence;
7. stop the service once;
8. verify zero pollers;
9. quarantine or remove only exactly enumerated known generated source
   `__pycache__/` and `.pyc` residue;
10. install the corrected repository artifact;
11. run `daemon-reload`;
12. start the service once;
13. prove exactly one poller;
14. trigger normal import/runtime activity;
15. prove `/opt/aios-src` remains completely clean;
16. prove bytecode appears beneath the approved runtime cache;
17. verify PostgreSQL and Storage remain unchanged and operational; and
18. do not reboot.

No step above is executed or authorized by this closure package.

## Future rollback

If the corrected production service fails:

1. stop the corrected service;
2. restore the prior Stage 9.2.2 installed unit;
3. run `daemon-reload`;
4. start once; and
5. verify exactly one polling process.

The disposable runtime cache may remain. No source, runtime configuration,
database/schema, Docker, Storage, or business-data rollback is needed or
authorized.

## Later-stage boundaries

Stage 9.2.4 retains the complete Git exclusion audit for secrets, database
data, logs, backups, and original business files. Stage 9.3.1 retains README,
CHANGELOG, capability, and operational-claim reconciliation.
