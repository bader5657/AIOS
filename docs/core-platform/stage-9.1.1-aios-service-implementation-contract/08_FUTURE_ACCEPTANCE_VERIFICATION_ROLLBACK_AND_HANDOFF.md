# Future Acceptance, Verification, Rollback, and 9.1.2 Handoff

## Stage 9.2.1 acceptance criteria

The future unit must be syntactically valid, invoke the existing entrypoint, use the approved environment and runtime identity, respect source/runtime separation, embed no secrets, authorize no duplicate polling topology, write no runtime data to Git, and introduce no application semantics, Brain, or later-phase behavior.

## Stage 9.2.2 verification criteria

Controlled VPS evidence must prove service installation/start, active state, exactly one Telegram polling process, reboot activation, systemctl/journalctl visibility, clean stop/start, approved invalid-config behavior, PostgreSQL availability interaction, Storage accessibility, and absence of duplicate manual polling.

## Rollback principle

Rollback is service-local: stop/disable the new service, restore the prior approved unit state if one exists, daemon-reload, and restart only with authority. Application service rollback must not roll back PostgreSQL data, stored originals, manifests, Registry rows, Events, or Core results.

## Binding 9.1.2 decisions

Stage 9.1.2 must approve exactly one tracked unit path, installed unit path, interpreter/virtual environment and ExecStart, WorkingDirectory, runtime user/group, EnvironmentFile declaration and permissions, restart/restart-delay/start limits, single-polling enforcement procedure, network/Docker/PostgreSQL ordering, shutdown timeout/signal behavior, compatible hardening directives, installation procedure, health evidence, and operational rollback commands.

`PRODUCTION / VPS EXECUTION = PROHIBITED` until separate later authority is active.
