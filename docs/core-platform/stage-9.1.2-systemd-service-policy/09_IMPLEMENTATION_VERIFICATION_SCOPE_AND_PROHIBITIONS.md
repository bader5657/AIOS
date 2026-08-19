# Implementation, Verification Scope, and Prohibitions

## Future Stage 9.2.1 boundary

Candidate scope is exactly `deploy/systemd/aios.service`, plus only narrowly approved static unit tests or operator documentation proven necessary in the separate implementation approval. No Python, Docker Compose, PostgreSQL, migration, runtime environment, or VPS change is implied.

Acceptance requires syntactically valid unit structure, all exact values in this policy, no secrets, existing module entrypoint, one-process topology, source/runtime separation, local/static validation, and no later-phase behavior.

## Future Stage 9.2.2 boundary

Separate production authority must cover install, daemon-reload, enable, start, active/MainPID/process inspection, journald, PostgreSQL and Storage access, clean stop/start, invalid-config evidence, controlled reboot, automatic reactivation, and post-reboot single polling.

## Prohibited scope

Stage 9.1.2 creates no unit, runtime/config/test/Docker/database change, system user, directory, permission, systemctl action, VPS access, Telegram polling, migration, monitoring stack, HTTP endpoint, Brain, Memory, Specialist Router, business behavior, retry, broker, queue, or application container.
