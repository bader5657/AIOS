# Interpreter, Import Probe, and Future Ordering Contract

## Existing candidates inspected

Read-only, no-network import probes inspected:

| Existing interpreter | Python | httpx | Required imports | Decision |
|---|---|---|---|---|
| `/opt/aios/runtime/venv/bin/python` | `3.12.3` | `0.28.1` | `PASS` | `SELECTED` |
| `/opt/aios/runtime/.venv/bin/python` | `3.12.3` | `0.28.1` | `PASS` | not selected |
| `/opt/aios/runtime/verification/stage-0.15-venv/bin/python` | `3.12.3` | `0.28.1` | `PASS` | verification-only; not selected |

The selected executable has `sys.prefix=/opt/aios/runtime/venv`. No package
installation or dependency change is required.

## Mandatory future no-inference probe

Before any future session ID or journal creation, the harness must invoke
`/opt/aios/runtime/venv/bin/python`, bind the resolved repository root
`/home/aiosadmin/AIOS` at `sys.path[0]`, and then:

1. import `httpx` and require `httpx.__version__ == "0.28.1"`;
2. import `core.ingestion.semantic_projection`;
3. import `core.core_to_brain_mapper`;
4. import `core.brain.schema_binding`;
5. import `core.brain.staging_composition`; and
6. resolve each repository module `__file__` and require component-aware
   containment beneath exactly `/home/aiosadmin/AIOS`.

The accepted probe resolved the modules respectively to:

- `/home/aiosadmin/AIOS/core/ingestion/semantic_projection.py`
- `/home/aiosadmin/AIOS/core/core_to_brain_mapper.py`
- `/home/aiosadmin/AIOS/core/brain/schema_binding.py`
- `/home/aiosadmin/AIOS/core/brain/staging_composition.py`

Interpreter selection does not replace root, clean-source, synchronization, or
module identity checks. No provider construction, network call, session, or
journal is part of the probe.

No system or venv package installation, copied site-packages, dependency
vendoring, symlinked dependency, persistent `PYTHONPATH`, shell-profile change,
new environment, repository source/package modification, or arbitrary alternate
interpreter is authorized.

## Mandatory future ordering

One separately reauthorized attempt must perform:

1. accepted privileged evidence verification;
2. a fresh lightweight network drift check;
3. exact authoritative interpreter verification;
4. the `httpx==0.28.1` probe;
5. process-local repository-root binding at `sys.path[0]`;
6. the full repository module import identity gate;
7. only then generate a new session ID;
8. exclusive-create a new journal;
9. full fresh session preflight;
10. construct one composition; and
11. execute the two fixed authorized requests.

Any mismatch stops before session admission. A future attempt requires a fresh
single-use execution authority, session ID, and journal.

