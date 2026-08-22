# Single-Poller Cutover, Corrected Unit, and Effective Verification

## Authorized transition

The only polling transition is:

`1 → 0 → 1`

1. confirm the current service owns exactly one poller;
2. stop `aios.service` once;
3. prove zero matching pollers and no alternate launcher;
4. complete approved bytecode quarantine;
5. install the corrected unit;
6. run `systemctl daemon-reload`;
7. verify the effective unit;
8. start `aios.service` once; and
9. prove exactly one systemd-owned poller.

Old and new polling processes must never overlap. No extra restart cycle and
no reboot are authorized.

## Corrected-unit installation

Install only the repository artifact with SHA-256:

`02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281`

to:

`/etc/systemd/system/aios.service`

Required installed metadata is `root:root 0644`. Copy/install from the exact
approved artifact; direct editing of the installed unit is prohibited.

## Effective unit gate

After daemon reload and before start, verify the effective service contains:

```ini
Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache
ReadOnlyPaths=/opt/aios-src
```

and preserves every prior Stage 9.1.2 value, including User/Group,
WorkingDirectory, EnvironmentFile, ExecStartPre, exactly one ExecStart,
restart/start-limit/shutdown values, hardening, enablement, and Docker/network
ordering. No `ReadWritePaths` exception for source may exist.

## Controlled start evidence

After the one authorized start, require:

- active/running service;
- non-zero MainPID owned by `aiosadmin`;
- interpreter `/opt/aios/runtime/venv/bin/python`;
- exactly one `core.adapters.telegram.main` process;
- stable NRestarts;
- no predecessor or alternate poller;
- no Telegram conflict;
- no immediate source-write or permission failure; and
- startup visible in journald.

Verify `PYTHONPYCACHEPREFIX` from the effective service/process environment
using a name-and-exact-value-only method that does not print any other
environment variable or secret. Verify `ReadOnlyPaths` through effective
systemd properties and normal runtime behavior; no tracked-source write probe
is authorized.
