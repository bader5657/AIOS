# Import, Network, and Pre-Session Gate Contract

## Repository root and process-local binding

The only approved repository root is `/home/aiosadmin/AIOS`. Before any
`core.*` import, the future temporary `/tmp` harness must perform the equivalent
of:

```python
from pathlib import Path
import sys

REPO_ROOT = Path("/home/aiosadmin/AIOS").resolve()

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
```

The root must exist, be a directory, not be a symlink, and resolve exactly to
`/home/aiosadmin/AIOS`. The repository must be clean and satisfy
`HEAD == main == origin/main`.

After binding, the harness must import and resolve `__file__` for:

- `core.ingestion.semantic_projection`
- `core.core_to_brain_mapper`
- `core.brain.schema_binding`
- `core.brain.staging_composition`

Every resolved module realpath must be beneath the exact approved root. A
module from `/tmp`, `site-packages`, `/opt/aios-src`, another checkout, or
another repository root is rejected. Any root, import, or module identity
failure stops before session ID or journal creation.

No persistent `PYTHONPATH`, shell profile change, `.pth` file, editable or
other repository installation, package metadata modification, copied module,
alternate checkout, or repository symlink is authorized. The binding is local
to the temporary harness process and occupies `sys.path[0]` when insertion is
required. No repository import may precede it.

## Network evidence and mandatory ordering

The accepted privileged evidence is
`/opt/aios/runtime/intelligence/staging/level-b-sessions/PRESESSION_PRIVILEGED_NETWORK_PREFLIGHT.txt`
with SHA-256
`6f284ae58e94e24f104fba7a5a671958b3d02e943f28e9af3548e948dd816d6d`.
The future harness must not run `sudo`.

Before session creation it must freshly verify, without privilege: no host
listener on 11434; no published staging port; attachment to only the approved
`aios-ollama-runtime` network; absent acquisition network; IP
`172.31.63.2`; and unchanged staging Docker socket. Drift stops before session
creation and returns control to privileged-preflight governance.

The mandatory order is:

1. verify privileged evidence identity and hash;
2. perform the lightweight network drift check;
3. verify the repository root and clean synchronized checkout;
4. bind the root into `sys.path[0]`;
5. import the required modules;
6. verify every module identity;
7. only then generate a new session ID;
8. only then exclusive-create a new journal;
9. run full fresh session preflight;
10. create one composition; and
11. execute up to exactly two authorized synthetic requests.

