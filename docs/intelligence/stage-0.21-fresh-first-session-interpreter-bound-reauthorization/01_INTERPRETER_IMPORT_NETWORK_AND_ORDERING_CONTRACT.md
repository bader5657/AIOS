# Interpreter, Import, Network, and Ordering Contract

The future harness must be invoked with exactly
`/opt/aios/runtime/venv/bin/python`. It must reject `/usr/bin/python3`, generic
`python3` or `python`, verification-only or temporary venvs, copied
environments, and every other interpreter unless separately governed.

Before session creation it must require literal
`sys.executable == "/opt/aios/runtime/venv/bin/python"`, Python `3.12.3`, and
`httpx.__version__ == "0.28.1"`. No package install/upgrade, venv creation,
site-packages copy, vendoring, dependency/requirements change, or persistent
environment change is authorized.

The only repository root is `/home/aiosadmin/AIOS`. Before repository imports,
the harness must resolve it exactly and bind it process-locally at
`sys.path[0]`. Interpreter selection does not replace source binding or identity
verification.

It must import and verify resolved `__file__` containment beneath that exact
root for:

- `core.ingestion.semantic_projection`
- `core.core_to_brain_mapper`
- `core.brain.schema_binding`
- `core.brain.staging_composition`

Any interpreter, version, dependency, root, import, clean-source,
synchronization, or module identity mismatch stops before session ID or journal
creation.

The accepted privileged evidence is
`/opt/aios/runtime/intelligence/staging/level-b-sessions/PRESESSION_PRIVILEGED_NETWORK_PREFLIGHT.txt`
with SHA-256
`6f284ae58e94e24f104fba7a5a671958b3d02e943f28e9af3548e948dd816d6d`.
The future harness must not run `sudo`.

The mandatory pre-session order is:

1. verify the privileged evidence identity and hash;
2. perform a fresh lightweight network drift check;
3. verify the exact authoritative interpreter identity;
4. verify Python `3.12.3`;
5. verify `httpx==0.28.1`;
6. bind the repository root into `sys.path[0]`;
7. import the required repository modules;
8. verify all module identities and clean synchronized source;
9. only then generate a new session ID;
10. exclusive-create a new journal;
11. run full fresh session preflight;
12. create one composition; and
13. execute exactly the two authorized synthetic requests.

No journal may exist before interpreter/import identity passes. Network drift
stops before session creation and returns control to network governance.

