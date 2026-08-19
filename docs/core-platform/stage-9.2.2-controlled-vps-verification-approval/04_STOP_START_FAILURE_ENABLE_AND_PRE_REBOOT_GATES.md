# Stop, Start, Failure, Enablement, and Pre-Reboot Gates

A controlled `systemctl stop aios.service` must complete within the approved
30-second timeout, leave no matching or orphan polling process, and delete no
data. A subsequent start must return one healthy service/MainPID/poller with no
conflict and usable journal evidence.

`Restart=on-failure` is process recovery, not business retry. Deliberate crash
simulation is not required by this approval: exact effective-directive
verification plus observed absence of a restart loop is sufficient. Any later
destructive failure injection requires separate explicit authority.

Invalid-config behavior must use existing static/local ExecStartPre evidence
unless a safe transient verification context can prove that a blank token or
Registry DSN prevents application startup without modifying production
`runtime.env`, exposing secrets, or causing an outage. Production secret/config
mutation is not authorized merely to repeat this test.

Only after initial health, clean stop/start, and single-polling verification
pass may the executor run `systemctl enable aios.service` and verify enabled
state.

Reboot is prohibited until all of these gates pass:

- known source revision and valid runtime environment;
- healthy PostgreSQL and accessible Storage;
- exact installed unit and valid systemd analysis;
- clean start, stop, and start cycle;
- exactly one polling process and no conflict;
- observable journal without secret leakage;
- enabled service;
- documented rollback procedure;
- confirmed post-reboot SSH/reconnection access;
- understood existing Docker/PostgreSQL reboot behavior.

Any failed pre-reboot gate cancels reboot authority for the cycle.
