# Focused Test and Verification Contract

## Exact test scope

Only `tests/unit/core_platform/test_aios_systemd_service.py` may change. Its
future assertions must prove at minimum:

- exact `Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`;
- exactly one `PYTHONPYCACHEPREFIX` directive;
- exact `ReadOnlyPaths=/opt/aios-src`;
- exactly one `ReadOnlyPaths` directive;
- both directives occur under `[Service]`;
- `EnvironmentFile=/opt/aios/runtime/config/runtime.env` is unchanged;
- WorkingDirectory, ExecStart, User, Group, restart, start-limit, shutdown,
  hardening, install target, and network/Docker ordering remain unchanged;
- exactly one ExecStart and no second service/process topology;
- no `ReadWritePaths` authority for `/opt/aios-src`;
- no `PYTHONDONTWRITEBYTECODE` unless separately authorized;
- no instruction to place `PYTHONPYCACHEPREFIX` in `runtime.env`; and
- no wrapper, containerization, retry, migration, source-write, secret,
  logging-stack, or monitoring-stack authority is introduced.

The existing strict section and exact key-set parsing can cover this delta.
No third repository path is needed.

## Future verification matrix

The implementation branch must run and record:

1. the focused service-unit test;
2. all Stage 9 critical service tests;
3. Stage 8 regression tests;
4. Core regression tests;
5. Domain regression tests;
6. compile/static verification;
7. dependency/import-boundary audit;
8. prohibited-source/static audit;
9. `git diff --check`;
10. exact two-path closed-world diff verification; and
11. supplementary `systemd-analyze verify` when available locally.

Local `systemd-analyze verify` findings caused only by absent production paths,
users, dependencies, or environment files must be separated from unit syntax
or directive defects. The local host must not be modified to imitate
production. No production network, Telegram, PostgreSQL, or Storage access is
required for repository implementation verification.

## Acceptance gate

Implementation is acceptable only if both directives are exact, every prior
service-policy assertion remains satisfied, all required verification passes,
the diff contains exactly the two authorized paths, and runtime/application
semantics remain unchanged.
