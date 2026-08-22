# Local Change Disposition, Rollback, and Prohibitions

The observed local `.gitignore` edit adds only archive exclusions:
`AIOS.tar.gz`, `AIOS.zip`, `*.tar.gz`, and `*.zip`. It is classified as a
still-useful production-local protection, not a secret-bearing change. The
approved deployment revision does not supersede it. It must be preserved as a
patch and reviewed later, but it must not silently reappear in the exact
deployment worktree.

Rollback evidence must be operator-controlled under
`/opt/aios/runtime/rollback/stage-9.2.2/source/` and contain the predecessor
branch, predecessor SHA, remote URLs, the `.gitignore`-only patch, and patch
SHA-256. If alignment fails before service cutover, checkout the predecessor
SHA and restore the preserved `.gitignore` state only if required. Rollback
does not authorize a service restart or any database or runtime-data rollback.

This approval prohibits stopping, restarting, reloading, enabling, disabling,
or replacing `aios.service`; rebooting; killing or duplicating Telegram
polling; changing runtime configuration or secrets; modifying either runtime
virtual environment; installing packages; running migrations; modifying
PostgreSQL, Storage, permissions, or runtime data; `git reset --hard` before
preservation; `git clean -fd`; force-push; history rewrite; historical sprint
merge; and beginning Stage 9.2.3.

