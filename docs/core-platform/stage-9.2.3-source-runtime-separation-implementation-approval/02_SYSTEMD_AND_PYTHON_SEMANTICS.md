# systemd and Python Semantics

## Directive placement

Both approved directives are execution-environment and filesystem-namespace
settings for the service process and therefore belong under `[Service]`:

- `Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`
- `ReadOnlyPaths=/opt/aios-src`

`Environment=` and `EnvironmentFile=` may coexist. The explicit cache-prefix
assignment neither changes nor replaces the required application/runtime
configuration file.

## Read-only source semantics

`ReadOnlyPaths=/opt/aios-src` creates a read-only view of that absolute path in
the service mount namespace. It does not remove the path, prevent read or
execute access, invalidate `WorkingDirectory=/opt/aios-src`, prevent Python
from importing modules there, or constrain the separate
`/opt/aios/runtime/cache/pycache` hierarchy.

No `ReadWritePaths=` exception beneath `/opt/aios-src` is needed or authorized.
The application writes original files and Manifests under `/opt/aios/data`,
uses operating-system temporary storage for Telegram downloads, and uses
journald rather than source-tree log files.

`PrivateTmp=true` only supplies private temporary-directory views. It does not
hide or make the approved `/opt/aios/runtime/cache/pycache` path read-only.

`SYSTEMD COMPATIBILITY = PASS`

`PRIVATETMP COMPATIBILITY = PASS`

`SOURCE READ-ONLY COMPATIBILITY = PASS`

## CPython semantics

The approved production interpreter is CPython 3.12.3. CPython supports
`PYTHONPYCACHEPREFIX`; when set, imported-module bytecode is written to a
parallel cache hierarchy rooted at the configured path instead of adjacent
`__pycache__` directories in application package directories.

Imports continue from `/opt/aios-src`, while generated `.pyc` becomes
disposable runtime state beneath `/opt/aios/runtime/cache/pycache`. Loss of the
cache causes regeneration only and changes no business or application
semantics.

`PYTHON COMPATIBILITY = PASS`

## Runtime semantic preservation

There is no change to Telegram ingestion, Registry, Event Engine, AIOS Core,
retry, deduplication, compensation, persistence, database behavior, or other
business logic. The delta changes only bytecode placement and service-level
source writability.
