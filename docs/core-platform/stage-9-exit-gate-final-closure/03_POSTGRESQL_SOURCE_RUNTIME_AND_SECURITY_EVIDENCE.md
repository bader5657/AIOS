# PostgreSQL, Source/Runtime, and Security Evidence

## PostgreSQL operational boundary

- container: `aios-postgres`, `HEALTHY`;
- host endpoint: `127.0.0.1:5432`;
- public exposure: `NONE`;
- production Registry DSN: present and nonempty without disclosure;
- accepted production connectivity evidence: `PASS`;
- persistent data: `/opt/aios/docker/postgres/data`, outside source;
- Stage 9 migration: `NONE`; and
- unintended schema/database/data mutation: `NONE`.

## Source/runtime separation

- source: `/opt/aios-src`;
- runtime: `/opt/aios`;
- service source policy: `ReadOnlyPaths=/opt/aios-src`;
- cache policy:
  `PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`;
- cache ownership/mode: `aiosadmin:aiosadmin 0750`;
- source status after normal runtime operation: `CLEAN`;
- source bytecode/residue: `NONE`; and
- generated runtime `.pyc`: outside source.

## Security and exclusion result

Production secrets, host SSH private keys, PostgreSQL data, database dump or
backup runtime state, rollback artifacts, original business files, runtime
Manifests, runtime cache, and temporary runtime state are outside Git/source.
`.gitignore` defense-in-depth hardening is accepted and intact.

- confirmed production secret exposure: `NONE DETECTED`;
- credential rotation: `NOT REQUIRED`;
- protected-category conformance: `PASS`; and
- Stage 9 security correction required: `NO`.
