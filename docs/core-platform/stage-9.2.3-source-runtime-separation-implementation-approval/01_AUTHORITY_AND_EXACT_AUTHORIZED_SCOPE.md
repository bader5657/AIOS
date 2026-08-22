# Authority and Exact Authorized Scope

## Authority trace

1. The Blueprint separates `/opt/aios-src` source from `/opt/aios` runtime.
2. Stage 9.1.2 fixes all service identity, execution, lifecycle, environment,
   restart, monitoring, and single-polling values.
3. Stage 9.2.1 implements and closes the current service artifact at Git blob
   `ace763735417d196f3841fb526d76b4e593fbbc3`.
4. Stage 9.2.2 proves production operation and defers bounded generated Python
   bytecode residue to Stage 9.2.3.
5. The Stage 9.2.3 service-policy correction, activated by merge
   `9da47009e7f7b92f1022c6daf2b4393fd48d7263`, authorizes exactly the cache
   prefix and read-only source directives.
6. This package grants the separate repository implementation authority
   required by the Execution Plan. It grants no production authority.

## Exact closed-world repository scope

Only these paths are authorized:

1. `deploy/systemd/aios.service`
2. `tests/unit/core_platform/test_aios_systemd_service.py`

`AUTHORIZED PATH COUNT = 2`

If implementation requires any third path, implementation must stop with:

`STAGE 9.2.3 SCOPE EXPANSION REQUIRED`

## Exact service delta

The future `deploy/systemd/aios.service` change must add exactly these two
directives under its existing `[Service]` section:

```ini
Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache
ReadOnlyPaths=/opt/aios-src
```

There is currently no `Environment=` entry. The new structural environment
directive coexists with and does not replace the existing exact declaration:

`EnvironmentFile=/opt/aios/runtime/config/runtime.env`

No `runtime.env` modification or cache-prefix declaration in that file is
authorized.

## Exact runtime path policy

Future production authority may create only:

`/opt/aios/runtime/cache/pycache`

with owner/group `aiosadmin:aiosadmin` and directory mode `0750`. This package
does not create it or authorize production execution.

## Closed-world prohibitions

No WorkingDirectory, ExecStart, interpreter, EnvironmentFile, User, Group,
restart, start-limit, shutdown, hardening, logging, monitoring, polling,
network/Docker ordering, migration, Python runtime code, application behavior,
PostgreSQL, Storage, Docker Compose, Brain, Memory, Specialist, wrapper, second
service, or second ExecStart change is authorized.
