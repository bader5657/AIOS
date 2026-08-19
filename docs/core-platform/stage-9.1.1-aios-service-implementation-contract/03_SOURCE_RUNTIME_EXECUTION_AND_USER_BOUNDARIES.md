# Source, Runtime, Execution, and User Boundaries

The service must respect Blueprint separation between `/opt/aios-src` and `/opt/aios`. Source checkout, deployed executable/runtime material, configuration, secrets, logs, backups, database data, and original files must not be conflated.

The conceptual ExecStart target is the existing Telegram entrypoint, currently expressible as module invocation of `core.adapters.telegram.main`. No second operational entrypoint is authorized. The exact interpreter, virtual environment, absolute command, Python path, deployed-code location, and WorkingDirectory remain 9.1.2 decisions because the `/opt/aios-src` → `/opt/aios` deployment procedure is not yet established.

The future service must use a dedicated non-root runtime identity unless a separate explicit decision authorizes otherwise. It requires only:

- read/execute access to approved application runtime material;
- read access to runtime configuration;
- write access to approved `/opt/aios/data/documents/...` locations; and
- no broad source-tree or host filesystem write authority.

The standard system location `/etc/systemd/system/aios.service` is the expected installation candidate, but exact installation location and the single tracked repository artifact path remain binding 9.1.2 decisions. No duplicate authoritative unit copy is permitted.
