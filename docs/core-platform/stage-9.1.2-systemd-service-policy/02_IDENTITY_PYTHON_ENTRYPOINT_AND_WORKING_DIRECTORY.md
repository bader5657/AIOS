# Identity, Python, Entrypoint, and Working Directory

The future unit policy is:

- `Type=simple`
- `User=aiosadmin`
- `Group=aiosadmin`
- Python environment: dedicated runtime virtual environment
- interpreter: `/opt/aios/runtime/venv/bin/python`
- `ExecStart=/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`
- `WorkingDirectory=/opt/aios-src`

`aiosadmin` is the existing operational non-root identity. The service requires no sudo action during runtime and receives no additional group or filesystem authority from the unit.

The source checkout is read/execute-only from the service perspective. Dependencies live in the runtime virtual environment. Runtime data and secrets remain under `/opt/aios`; the module invocation uses the existing entrypoint and introduces no wrapper or shell indirection.
