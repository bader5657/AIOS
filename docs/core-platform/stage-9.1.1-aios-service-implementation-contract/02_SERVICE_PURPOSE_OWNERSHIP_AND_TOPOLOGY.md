# Service Purpose, Ownership, and Topology

`aios.service` is the single authoritative host-level systemd service that starts the existing AIOS Telegram application entrypoint and owns its production process lifecycle.

The approved conceptual topology is:

- one host-level `aios.service`;
- one Python AIOS process;
- one Telegram `Application.run_polling()` lifecycle inside that process; and
- one separate PostgreSQL Docker Compose service.

Systemd owns start, stop, process supervision, later approved restart behavior, enablement, and reboot activation. Telegram Adapter remains the polling owner inside the Python process.

The service does not own business logic, Storage/Metadata/Manifest semantics, Registry semantics, Event Engine semantics, AIOS Core semantics, PostgreSQL container lifecycle, migrations, Brain, or later-phase behavior.

Multiple application workers, multiple polling processes, supervisor pools, Celery, schedulers, queue consumers, application containers, and background services are outside this contract.
