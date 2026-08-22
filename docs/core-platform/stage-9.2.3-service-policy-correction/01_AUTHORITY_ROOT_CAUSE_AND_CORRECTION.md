# Authority, Root Cause, and Exact Policy Correction

## Authority trace

The controlling authority is applied in this order:

1. The Blueprint fixes `/opt/aios-src` as source repository and `/opt/aios` as
   runtime, with runtime secrets, database data, logs, backups, and original
   business files excluded from Git.
2. The Execution Plan names Stage 9.2.3 as the deployment-separation step and
   requires deployment procedure, reviewed configuration, and runtime-path
   verification before completion.
3. Stage 9.1.1 requires the service to avoid runtime writes in source.
4. Stage 9.1.2 requires `/opt/aios-src` to be read/execute-only from the service
   perspective, but its exact approved unit policy contains neither
   `PYTHONPYCACHEPREFIX` nor `ReadOnlyPaths`.
5. Stage 9.2.1 implemented and statically verified that earlier exact policy.
6. Stage 9.2.2 proved the service lifecycle and accepted generated
   `__pycache__/` and `.pyc` only as bounded residue whose permanent handling
   belongs to Stage 9.2.3.
7. The Project Owner's Stage 9.2.3 evaluation and this correction decision
   provide the missing narrow policy authority.

Implementation of either new directive remains blocked until this governance
package is normally merged and active.

## Root cause

The approved command imports application modules directly from the checkout:

`/opt/aios/runtime/venv/bin/python -m core.adapters.telegram.main`

with:

`WorkingDirectory=/opt/aios-src`

CPython 3.12 normally stores imported-module bytecode in `__pycache__`
directories beside source when those directories are writable. The service
identity can currently write there. No application semantic defect or Python
source change is involved.

## Corrected bytecode policy

`AIOS PYTHON BYTECODE CACHE LOCATION = /opt/aios/runtime/cache/pycache`

The future unit must contain exactly:

`Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`

This structural deployment configuration belongs in the tracked systemd unit,
not in `/opt/aios/runtime/config/runtime.env`. CPython 3.12 supports
`PYTHONPYCACHEPREFIX` and uses it to place `.pyc` in a parallel cache hierarchy
outside package directories. No source change, wrapper, interpreter change,
WorkingDirectory change, or ExecStart change is authorized.

## Corrected source-access policy

`AIOS SERVICE SOURCE ACCESS = READ/EXECUTE ONLY`

The future unit must contain exactly:

`ReadOnlyPaths=/opt/aios-src`

This enforces the source boundary in the service mount namespace. Operator
deployment access remains distinct from runtime service access. Broad
recursive source `chmod` or `chown` is not the primary enforcement mechanism
and is not authorized by this package.

## Runtime cache ownership and lifecycle

| Property | Policy |
|---|---|
| Path | `/opt/aios/runtime/cache/pycache` |
| Owner/group | `aiosadmin:aiosadmin` |
| Directory mode | `0750` |
| Service access | `READ/WRITE` |
| World-write | `PROHIBITED` |
| Classification | `DISPOSABLE OPERATIONAL CACHE` |

The cache may survive service restart and reboot, but cache correctness is not
business correctness. Its loss must not remove canonical state. It has no
backup requirement and no database, Registry, Manifest, original-file, or
rollback meaning. No automatic cleanup daemon is approved.
