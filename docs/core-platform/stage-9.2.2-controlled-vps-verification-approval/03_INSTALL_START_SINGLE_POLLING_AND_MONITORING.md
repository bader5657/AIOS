# Installation, Start, Single Polling, and Monitoring

After every preflight gate passes, the only approved installation mutations
are:

1. install the reviewed tracked unit at `/etc/systemd/system/aios.service` with
   systemd-appropriate ownership and mode;
2. run `systemctl daemon-reload`;
3. compare the installed unit with the approved artifact;
4. run `systemd-analyze verify` and inspect effective unit properties;
5. start `aios.service` only after the installed artifact is exact.

No other unit, template, helper, service, runtime source, environment content,
Docker configuration, or database object may change. The unit may not own or
start Docker Compose/PostgreSQL.

Initial-start evidence must prove active/running state, a non-zero MainPID,
`aiosadmin` ownership, the exact approved command line, no restart loop, a
successful preflight, and no secrets in the journal.

Single-polling evidence must prove:

- exactly one active `aios.service`;
- exactly one MainPID;
- exactly one matching foreground Python module process;
- zero manual, container, supervisor, template, or alternate pollers;
- zero Telegram polling-conflict evidence in the journal.

The mandatory result is `ACTIVE TELEGRAM POLLING INSTANCE COUNT = 1`. No
business or user test message is authorized.

Minimum monitoring is systemd-native only: `systemctl status`,
`systemctl is-active`, `systemctl is-enabled`, and
`journalctl -u aios.service`. Health means process/service state, one poller,
journal visibility, PostgreSQL availability, and Storage access; it is not
business-pipeline success. No HTTP health endpoint or monitoring stack is
authorized.
