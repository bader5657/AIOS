# Restart, Rate Limit, Shutdown, and Enablement

The exact future process policy is:

- `Restart=on-failure`
- `RestartSec=10s`
- `StartLimitIntervalSec=300s`
- `StartLimitBurst=5`
- default systemd `SIGTERM` shutdown; no custom `KillSignal`
- `TimeoutStopSec=30s`
- `KillMode=control-group`

The rate limit bounds permanent configuration crash loops. Deliberate operator stop is not an application failure. Process restart is not business retry and must not replay failed ingestion; pipeline/business `RETRY = NONE` remains binding.

After separately approved installation and operational verification, the service must be enabled for reboot activation. Installation, enablement, and activation are distinct actions. Stage 9.1.2 performs none of them.
