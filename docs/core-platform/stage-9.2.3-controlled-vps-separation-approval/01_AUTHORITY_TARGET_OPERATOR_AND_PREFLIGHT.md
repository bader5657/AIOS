# Authority, Target, Operator, and Read-Only Preflight

## Authority trace

The Blueprint source/runtime boundary, active Stage 9.1.2 service policy,
closed Stage 9.2.2 operational verification, active Stage 9.2.3 policy
correction, approved implementation, and repository closure are cumulative and
binding. This package adds only the production authority needed to apply the
already-reviewed repository artifact.

The exact repository authority is:

- main baseline: `9579083000a675a264ce482eaf7323df5840e111`;
- service Git blob: `8794ee77cea44dae5bb7f96d876d3a240b5a78ed`;
- service SHA-256:
  `02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281`.

The previously mistyped shorter blob value is invalid and must not be used.

## Authenticated operator model

- Required channel: `Bagus-PC → aiosadmin@aios-prod-01`
- Required server identity: `aios-prod-01`
- Required login identity: `aiosadmin`
- Privilege model: already-approved authenticated user with interactive sudo
  only for exact root-owned paths and systemd operations
- New SSH key installation: `PROHIBITED`

The executor must verify both client/operator context and server identity. If
Codex cannot authenticate directly, execution must be operator-assisted in the
already-authenticated Windows/VPS terminal. Authentication failure is not
authority to change `authorized_keys`.

## Mandatory read-only preflight

Before any mutation, record without exposing secrets:

- `hostname=aios-prod-01` and `whoami=aiosadmin`;
- interactive sudo availability;
- `aios.service` active and enabled;
- one non-zero MainPID and stable NRestarts;
- exactly one systemd-owned Telegram polling process and no alternate poller;
- active interpreter `/opt/aios/runtime/venv/bin/python`;
- PostgreSQL container healthy and host publication only at
  `127.0.0.1:5432`;
- approved Storage read/write capability;
- `/opt/aios/runtime/config/runtime.env` metadata `root:aiosadmin 0640`, with
  required-key presence verified name-only;
- source HEAD at the active approved deployment revision;
- installed-unit identity and existing rollback evidence; and
- availability of enough space for cache and rollback preservation.

No token, password, complete DSN, or environment content may be printed.

## Source integrity gate

Before mutation, `/opt/aios-src` must have:

- the expected active deployment HEAD;
- no tracked modification;
- no staged modification;
- no untracked or ignored content except independently classified generated
  `__pycache__/` directories and `.pyc` files.

Every generated residue path must be enumerated first. Any unknown residue,
source change, archive, environment file, business file, log, database file,
or unexplained ignored content stops execution with:

`STAGE 9.2.3 SOURCE INTEGRITY BLOCKED`
