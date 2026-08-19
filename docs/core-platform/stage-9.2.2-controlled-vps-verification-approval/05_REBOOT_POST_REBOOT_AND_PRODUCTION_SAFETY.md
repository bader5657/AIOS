# Reboot, Post-Reboot, and Production Safety

The Project Owner authorizes at most one controlled reboot in this verification
cycle, and only after every pre-reboot gate passes. No repeated reboot loop is
authorized.

After reconnection, evidence must prove:

- the expected host returned and source revision is unchanged;
- Docker is active and PostgreSQL is healthy under its existing policy;
- `aios.service` is enabled and active with a non-zero MainPID;
- one matching AIOS Python process and one Telegram polling instance exist;
- no manual, alternate, container, or duplicate unit poller exists;
- journal evidence shows clean reboot activation and no conflict;
- Storage remains accessible and production configuration remains protected;
- no migration ran and no runtime data entered Git.

Final single-polling proof is exactly:

- `ONE ENABLED SERVICE`;
- `ONE MAINPID`;
- `ONE MATCHING PYTHON PROCESS`;
- `ZERO ALTERNATE POLLING PROCESSES`;
- `ZERO TELEGRAM CONFLICT EVIDENCE`.

The verification must also confirm zero PostgreSQL schema/business-data,
original-file, Manifest, Registry-row, runtime-source, Stage 8 semantic,
Docker Compose, migration, or secret-content mutation. Only the approved unit
installation and systemd state transitions are expected external changes.
