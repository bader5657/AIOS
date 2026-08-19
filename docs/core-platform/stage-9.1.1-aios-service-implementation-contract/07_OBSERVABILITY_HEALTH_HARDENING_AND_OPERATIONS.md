# Observability, Health, Hardening, and Operations

Minimum authoritative observability is systemd-native:

- service state inspectable with `systemctl`;
- process stdout/stderr inspectable with `journalctl`.

Journald capture is sufficient for this service contract. Structured logs, persistent application log files, Prometheus, Grafana, web dashboards, and HTTP health servers are not required or authorized.

Operational health is distinct from business-pipeline success. Later evidence may combine active systemd state, one live polling process, valid configuration, PostgreSQL availability, storage accessibility, and journal output. The exact minimum health checklist belongs to 9.1.2 and verification to 9.2.2.

Systemd hardening directives are not added speculatively. 9.1.2 may approve minimal directives only after verifying that runtime configuration and approved Storage paths remain accessible.

Future daemon-reload, install, enable, start, stop, restart, disable, and rollback commands are operator procedures owned by 9.2.1 implementation/deployment approval and 9.2.2 runtime verification. Nothing in this package executes them.
