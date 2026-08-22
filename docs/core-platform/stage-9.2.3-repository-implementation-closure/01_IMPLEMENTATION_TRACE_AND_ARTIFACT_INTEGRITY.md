# Implementation Trace and Final Artifact Integrity

## Authority and PR trace

- Policy-correction merge:
  `9da47009e7f7b92f1022c6daf2b4393fd48d7263`
- Implementation-approval merge:
  `9080913fa8d4806ecf9512c88650c46fa9de77c0`
- Implementation PR: `#93`
- PR base: `9080913fa8d4806ecf9512c88650c46fa9de77c0`
- Implementation commit: `c4c3438db63deee512de6ed753a6861145c4e801`
- Implementation merge/closure baseline:
  `2c44dc84cb38dc51778f8a65f12a6e59683c74c9`

PR #93 changed exactly the two authorized paths:

1. `deploy/systemd/aios.service`
2. `tests/unit/core_platform/test_aios_systemd_service.py`

No third path changed. The service artifact delta was exactly two added lines
and no deletion.

## Artifact identity

- Service Git blob: `8794ee77cea44dae5bb7f96d876d3a240b5a78ed`
- Service SHA-256:
  `02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281`
- Focused test Git blob: `f25781069aa3846088213ac3181dac856ba11b1d`

The Git blob above is derived from the real merged artifact. It corrects the
transcription `8794ee77cea44dae5bb7f96d87d3a240b5a78ed`, which omits one `6`
and is not the repository object identity.

## Final directive integrity

The real tracked unit contains exactly once under `[Service]`:

```ini
Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache
ReadOnlyPaths=/opt/aios-src
```

Final review confirms:

- `EnvironmentFile=/opt/aios/runtime/config/runtime.env` is unchanged;
- `WorkingDirectory=/opt/aios-src` is unchanged;
- `ExecStart=/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`
  is unchanged and occurs exactly once;
- `User=aiosadmin` and `Group=aiosadmin` are unchanged;
- restart, shutdown, hardening, enablement, ordering, and single-polling policy
  is unchanged;
- `PYTHONDONTWRITEBYTECODE` is absent;
- `ReadWritePaths=/opt/aios-src` and any other source-write exception are
  absent; and
- both new directives are in `[Service]`, not `[Unit]` or `[Install]`.

`FINAL ARTIFACT INTEGRITY = PASS`
