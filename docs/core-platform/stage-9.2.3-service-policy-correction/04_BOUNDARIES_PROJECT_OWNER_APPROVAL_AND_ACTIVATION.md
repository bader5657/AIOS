# Boundaries, Project Owner Approval, Publication, and Activation

## Stage boundaries

Stage 9.2.3 remains limited to structural source/runtime separation. Complete
secret, database-data, log, backup, and original-business-file Git exclusion
audits remain owned by Stage 9.2.4.

README, CHANGELOG, capability, and operational-claim reconciliation remains
owned by Stage 9.3.1. This package changes none of those artifacts.

Brain, Memory, Specialist, n8n, Hermes, Traefik, application containerization,
retry, migration, new logging, and new monitoring remain outside scope.

## Project Owner decision

I, as Project Owner, approve the Stage 9.2.3 service-policy correction:

1. AIOS Python bytecode/cache is redirected to
   `/opt/aios/runtime/cache/pycache` via systemd
   `Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`.
2. The AIOS service receives read-only source enforcement through
   `ReadOnlyPaths=/opt/aios-src`.
3. Runtime cache ownership is `aiosadmin:aiosadmin`, mode `0750`.
4. No other Stage 9.1.2 service policy is changed.
5. One controlled service restart may be authorized later for verification.
6. No reboot is required.

This approval corrects policy only. Service-artifact implementation, tests,
VPS cache creation, unit installation, daemon reload, restart, residue
disposition, and runtime verification require their own later authority.

## Publication and activation

- Branch: `governance/stage-9.2.3-service-policy-correction`
- Baseline: `86d127f94494f1c18364035480302b9751c1d534`
- Allowed diff: governance records in this directory only
- Activation: normal merge of the dedicated governance PR

Post-merge audit must prove `HEAD == main == origin/main`, a clean tracked
worktree, this package present, governance-only merge scope, unchanged service
blob `ace763735417d196f3841fb526d76b4e593fbbc3`, and no VPS or production
mutation during the workflow.

After successful normal merge and audit:

`STAGE 9.2.3 SERVICE POLICY CORRECTION ACTIVE — READY FOR IMPLEMENTATION APPROVAL`
