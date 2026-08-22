# Production Verification Boundary

Stage 10.2.1 includes an operational suite for the exact baseline. Accepted
Stage 9 evidence should be reused where it still proves the current state.
Fresh production inspection is authorized only when necessary to establish
that accepted invariants remain current.

Any fresh check must be read-only and limited to evidence such as:

- deployed/accepted source SHA and authoritative service-artifact identity;
- effective service state, enabled state, process ownership, and single-poller
  count without changing them;
- systemctl/journalctl observation with secret/context minimization;
- PostgreSQL health/loopback placement and protected storage placement without
  querying or changing original business data;
- source/runtime separation, runtime rollback boundary, and protected-data
  location/permissions without content disclosure.

The following are prohibited:

- reboot, restart, stop/start, reload, enable/disable, installation, or cutover;
- migration, schema change, database mutation, test write, or source mutation;
- environment/secret change, runtime-file change, rollback action, or cleanup;
- production Telegram interaction or any action that creates business/runtime
  state.

If evidence shows that mutation is necessary, work stops before mutation and
requests separate exact authority. This package itself performs no VPS access.
