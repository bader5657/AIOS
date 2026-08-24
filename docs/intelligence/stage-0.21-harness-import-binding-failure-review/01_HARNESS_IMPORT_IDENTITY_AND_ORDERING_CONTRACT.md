# Harness Import Identity and Pre-Session Ordering Contract

## Accepted root and controlled binding

The sole accepted repository root is:

`/home/aiosadmin/AIOS`

Any future temporary `/tmp` operator harness must establish the resolved root
at `sys.path[0]` before importing any repository module:

```python
from pathlib import Path
import sys

REPO_ROOT = Path("/home/aiosadmin/AIOS").resolve()
sys.path.insert(0, str(REPO_ROOT))
```

Harness location must not influence repository import resolution. The harness
must not rely on current working directory, implicit or persistent
`PYTHONPATH`, shell launch location, copied modules, or an alternate checkout.
No package installation, editable install, `.pth` file, environment mutation,
repository symlink, dependency change, or `setup.py`/`pyproject` change is
authorized.

## Mandatory import identity gate

Before generating a session ID, admitting a session journal, or creating a
composition, the future harness must verify all of the following:

1. the accepted repository root exists;
2. its resolved realpath is exactly `/home/aiosadmin/AIOS`;
3. the checkout is clean and `HEAD`, local `main`, and `origin/main` are exactly
   synchronized;
4. after the explicit `sys.path[0]` binding, every required imported module has
   a resolved `__file__` beneath that exact root; and
5. no required module resolves from `/tmp`, `site-packages`, `/opt/aios-src`, or
   any other checkout.

The required modules are:

- `core.ingestion.semantic_projection`
- `core.core_to_brain_mapper`
- `core.brain.schema_binding`
- `core.brain.staging_composition`

Path comparison must use resolved absolute paths and a path-component-aware
containment test. A missing `__file__`, import error, dirty or unsynchronized
checkout, wrong realpath, or identity mismatch is a hard stop before session
admission. It must not consume a session ID or journal.

## Mandatory ordering for a future attempt

One separately reauthorized attempt must execute in this order:

1. verify the accepted operator privileged network evidence;
2. perform a fresh lightweight network drift check;
3. verify repository root binding, clean/synchronized source, and exact module
   identities;
4. only then generate a fresh session ID;
5. exclusive-create a fresh journal;
6. perform full fresh session preflight;
7. construct exactly one composition and one client/provider lifecycle; and
8. execute the authorized two-request session.

The future harness must not invoke `sudo`. If the lightweight checks differ
materially from the accepted privileged evidence, it must stop before session
creation and require a new operator privileged inspection.

