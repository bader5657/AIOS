# Single Polling, Logging, Health, and Reboot Evidence

Single-instance enforcement is operational: exactly one enabled `aios.service` is the sole authorized production launcher; it owns one MainPID and one `run_polling()` lifecycle. Manual direct production invocation, a second unit instance, application container, alternate supervisor, worker pool, or polling process is prohibited. No PID/file lock is required or authorized.

Stage 9.2.2 must prove:

- `systemctl is-active aios.service` succeeds;
- one non-zero systemd MainPID exists;
- exactly one matching AIOS Python module process exists;
- no parallel manual/container/supervisor polling process exists;
- journal startup evidence exists and Telegram conflict errors are absent;
- configured Registry database interaction succeeds;
- approved Storage paths are accessible to the runtime identity;
- clean stop/start succeeds;
- controlled reboot automatically reactivates exactly one polling process.

System defaults capture stdout/stderr in journald; explicit `StandardOutput`/`StandardError`, file logs, structured logging, Prometheus, Grafana, and HTTP health endpoints are unnecessary. Service health is operational evidence, not business-pipeline success.
