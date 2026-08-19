# Authority, Target, and Stop Conditions

The Core Platform Execution Plan requires runtime verification authority and an
operational verification record for Stage 9.2.2. Stage 9.1.1 established the
service contract, Stage 9.1.2 established the exact service policy, and Stage
9.2.1 implemented and closed the reviewed repository artifact.

The single approved production target identified by repository authority is:

- provider: Hostinger VPS;
- hostname: `aios-prod-01`;
- operating system: Ubuntu 24.04.4 LTS;
- systemd host with Docker and Docker Compose;
- PostgreSQL documented as a separate healthy container/service.

Credentials, addresses, secret values, and DSNs must never be recorded in
verification output.

Execution must stop without corrective mutation when any of these conditions
is found:

- existing installed unit is unauthorized or conflicts with the tracked unit;
- any competing Telegram polling process exists;
- `/opt/aios-src` is not at the explicitly authorized deployment revision;
- the runtime virtualenv is absent or incomplete;
- production configuration is missing, unsafe, or includes the test DSN;
- Storage is inaccessible to `aiosadmin`;
- PostgreSQL is unavailable;
- repository or service-artifact correction is required.

The respective dispositions are `EXISTING SERVICE CONFLICT`,
`DUPLICATE POLLING RISK`, `SOURCE DEPLOYMENT ALIGNMENT REQUIRED`,
`RUNTIME ENVIRONMENT PRECONDITION FAILED`,
`PRODUCTION CONFIG PRECONDITION FAILED`,
`REPOSITORY CORRECTION APPROVAL REQUIRED`, or
`SERVICE ARTIFACT CORRECTION REQUIRED`. No process may be killed and no
precondition may be silently repaired under this approval.
