# Rollback, Correction, and Prohibited Scope

If verification fails, rollback is service-local:

1. stop `aios.service`;
2. disable it if newly enabled;
3. restore an approved prior unit if one existed, otherwise remove only the
   newly installed unit;
4. run `systemctl daemon-reload`;
5. leave PostgreSQL and all runtime/business data untouched;
6. preserve journal and verification evidence;
7. do not start a manual poller without separate authority.

No database or data rollback is authorized.

If repository modification is necessary, execution stops with
`STAGE 9.2.2 REPOSITORY CORRECTION APPROVAL REQUIRED`. If the approved unit has
a contract defect, execution stops with
`STAGE 9.2.2 SERVICE ARTIFACT CORRECTION REQUIRED`; the installed unit must not
be edited ad hoc.

This approval prohibits Python/test/unit-artifact changes, Docker Compose
changes, PostgreSQL schema or migration work, environment or secret changes,
business-data changes, unrelated deployment, additional services, monitoring
stacks, HTTP health endpoints, retry, Brain, LLM/Ollama, n8n, Hermes/OpenClaw,
and SSH/security-policy changes. It does not authorize deleting or repairing a
competing process, source deployment, virtualenv, permissions, Storage,
PostgreSQL, or configuration prerequisite.
