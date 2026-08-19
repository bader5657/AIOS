# Single Polling, Restart, Reboot, and Shutdown

`EXACTLY ONE ACTIVE PRODUCTION TELEGRAM POLLING INSTANCE` is binding.

Systemd becomes the sole authoritative production process owner. Manual duplicate production startup, additional polling workers/containers, and a second enabled service instance are prohibited. A technical lock or PID mechanism is not inferred: 9.1.2 must choose the smallest sufficient enforcement procedure and later verification must prove exclusivity.

Systemd process restart is distinct from pipeline/business retry. Application retry remains `NONE`; a restarted process must not automatically replay a failed ingestion request. Exact `Restart=`, `RestartSec=`, rate limits, and start-limit behavior are deferred to 9.1.2.

After controlled installation and enablement, AIOS must automatically become active after VPS reboot. Stage 9.2.2 owns real reboot verification.

The existing Telegram library manages polling shutdown. The minimum future contract is ordinary systemd stop through SIGTERM with clean process termination. Exact stop timeout, kill mode/signal, and any escalation remain 9.1.2 decisions. Complex draining or cross-component rollback is not authorized.
