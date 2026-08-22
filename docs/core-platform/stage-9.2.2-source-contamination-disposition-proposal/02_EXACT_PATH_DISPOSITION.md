# Exact Path Disposition

No deletion is proposed. Before any move, record a path manifest with type,
ownership, mode, size, timestamp, and SHA-256 for regular files without logging
file contents.

Move these class C paths under the existing Stage 9.2.2 rollback area:

- `/opt/aios-src/.venv` to `/opt/aios/runtime/rollback/stage-9.2.2/source-contamination/source-.venv`
- `/opt/aios-src/AIOS.tar.gz` to `/opt/aios/runtime/rollback/stage-9.2.2/source-contamination/AIOS.tar.gz`
- `/opt/aios-src/AIOS.zip` to `/opt/aios/runtime/rollback/stage-9.2.2/source-contamination/AIOS.zip`

Move, rather than delete, these exact class D paths into a relative-path
quarantine rooted at
`/opt/aios/runtime/rollback/stage-9.2.2/source-contamination/cache/`:

- `/opt/aios-src/.pytest_cache`
- `/opt/aios-src/core/__pycache__`
- `/opt/aios-src/core/adapters/__pycache__`
- `/opt/aios-src/core/adapters/telegram/__pycache__`
- `/opt/aios-src/core/app/__pycache__`
- `/opt/aios-src/core/conversation/__pycache__`
- `/opt/aios-src/core/event/__pycache__`
- `/opt/aios-src/core/ingestion/__pycache__`
- `/opt/aios-src/core/mission/__pycache__`
- `/opt/aios-src/core/pipeline/__pycache__`
- `/opt/aios-src/core/registry/__pycache__`
- `/opt/aios-src/core/router/__pycache__`
- `/opt/aios-src/core/specialists/__pycache__`
- `/opt/aios-src/core/specialists/shoegabox/__pycache__`
- `/opt/aios-src/core/storage/__pycache__`
- `/opt/aios-src/tests/__pycache__`
- `/opt/aios-src/tests/unit/__pycache__`
- `/opt/aios-src/tests/unit/conversation/__pycache__`
- `/opt/aios-src/tests/unit/conversation_repository/__pycache__`
- `/opt/aios-src/tests/unit/event/__pycache__`
- `/opt/aios-src/tests/unit/pipeline/__pycache__`
- `/opt/aios-src/tests/unit/registry/__pycache__`
- `/opt/aios-src/tests/unit/storage/__pycache__`

Each quarantine destination must preserve the source-relative path so moves
are reversible and collision-free. The already-preserved `.gitignore` patch
remains at `/opt/aios/runtime/rollback/stage-9.2.2/source/gitignore.patch`.
After relocation, restore the tracked `.gitignore` through the controlled exact
checkout; do not reapply its production-local archive exclusions.

