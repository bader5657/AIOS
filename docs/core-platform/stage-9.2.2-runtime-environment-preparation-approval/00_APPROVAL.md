# Stage 9.2.2 Runtime Environment Preparation Approval

- Classification: `CONTROLLED RUNTIME ENVIRONMENT PREPARATION / NO SERVICE ACTIVATION`
- Approved source baseline: `4168e098612c930215a49028d4ca9fc200d21cfd`
- Source path: `/opt/aios-src`
- Target environment: `/opt/aios/runtime/venv`
- Creation interpreter: `/usr/bin/python3` at Python `3.12.3`
- Dependency authority: `/opt/aios-src/requirements.txt` at the approved baseline
- Installation scope: all and only the 11 exact pins in that requirements file
- Approval status: `PUBLISHED — ACTIVE` upon normal merge

The target must be absent before creation. Authority permits exactly
`/usr/bin/python3 -m venv /opt/aios/runtime/venv` followed by installation with
the target venv's pip using the approved requirements file. It prohibits global
or predecessor-environment installation, unpinned additions, editable install,
system Python upgrade, application start, Telegram polling, service/systemd
mutation, configuration or secret changes, database access or migration,
Storage changes, source changes, cutover, and Stage 9.2.3 work.

The executor must preserve `/opt/aios/runtime/.venv` and the active predecessor
process. Acceptance requires Python compatibility, `pip check`, exact critical
versions, safe imports, compile/static checks, focused non-production tests,
future ExecStart module resolution, a clean source tree, and the same single
predecessor poller throughout. Tests must not use production Telegram or a
production database.

If preparation fails, the predecessor remains untouched. The newly created
target may be quarantined under the existing Stage 9.2.2 rollback area; removal
is not authorized by this package. No database or data rollback applies.

I, as Project Owner, approve creation of the separate Stage 9 production
runtime environment at `/opt/aios/runtime/venv` using the exact dependency
declarations from the approved Stage 9.2.2 source revision. The existing
`/opt/aios/runtime/.venv` must remain untouched because it supports the active
predecessor poller. No service restart, configuration change, database change,
Telegram activation, source change, or application semantic change is
authorized.

`STAGE 9.2.2 RUNTIME ENVIRONMENT PREPARATION APPROVED — READY FOR CONTROLLED EXECUTION`
