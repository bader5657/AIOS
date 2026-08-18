# Exact Baseline and Repository Conventions

| Evidence | Result |
|---|---|
| `HEAD`, local `main`, local `origin/main` | `5a0cb10e10503739be1f7af8abfe4d1bdaf24493` |
| remote `refs/heads/main` | `5a0cb10e10503739be1f7af8abfe4d1bdaf24493` |
| Stage 5.2.2 closure merge | `5a0cb10e10503739be1f7af8abfe4d1bdaf24493` |
| Python runtime inspected | CPython `3.12.3` |
| Worktree before branch creation | clean |
| Current Registry runtime/migrations | absent |
| Current migration convention | absent |
| Current integration-test tree | absent |
| Test convention | standard-library `unittest`; package markers used in scoped test directories |
| Dependency authority file | `requirements.txt` |

No accepted migration convention conflicts with `migrations/postgres/`.
Historical PR #1 remains unrelated and non-blocking.
