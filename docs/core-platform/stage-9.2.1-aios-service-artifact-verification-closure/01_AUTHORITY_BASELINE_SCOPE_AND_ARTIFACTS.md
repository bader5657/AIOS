# Authority, Baseline, Scope, and Artifacts

Stage 9.1.1 established the authoritative service contract: one host-level
systemd-managed AIOS process, one Telegram polling lifecycle, separate source
and runtime trees, external configuration, and PostgreSQL remaining a separate
Docker Compose service. Stage 9.1.2 fixed the concrete unit values. The Stage
9.2.1 implementation approval authorized exactly:

- `deploy/systemd/aios.service`
- `tests/unit/core_platform/test_aios_systemd_service.py`

PR #82 merged those two files, and no other implementation path entered
`main`. The exact closure baseline is
`8796766703945445c7a887e7de425589765c29b2`.

The tracked service artifact is `deploy/systemd/aios.service`. Its future
installed target is `/etc/systemd/system/aios.service`. This closure authorizes
only documentation under this directory; it does not alter either implemented
artifact.

No Python runtime, configuration, Docker/Compose, database, migration, schema,
dependency, Blueprint, Roadmap, or architecture change is part of this closure.
