# Installation, Rollback, and Stage Boundaries

Stage 9.2.1 should use the minimum artifact model: one tracked unit file plus reviewed operator commands/documentation. No installation script is required by default. Any test or documentation path needs explicit Stage 9.2.1 scope approval.

The future controlled installation procedure is conceptually: validate the reviewed unit, install it at the approved system path, daemon-reload, and stop before activation unless the separate production authorization explicitly includes enable/start. Stage 9.2.1 is repository implementation and local/static verification; Stage 9.2.2 owns VPS installation/enablement/start/reboot evidence.

Rollback is service-local:

1. stop the service;
2. disable it if required;
3. restore the prior approved installed unit if one exists, otherwise remove only the newly installed unit under explicit authority;
4. daemon-reload;
5. restart only after authorization.

Service rollback never reverses PostgreSQL data, stored originals, Metadata, Manifests, Registry rows, Events, or Core results.

`PRODUCTION / VPS EXECUTION = PROHIBITED` in Stage 9.1.2.
