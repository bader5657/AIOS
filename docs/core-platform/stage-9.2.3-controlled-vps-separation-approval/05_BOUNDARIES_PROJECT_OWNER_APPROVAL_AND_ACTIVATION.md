# Boundaries, Project Owner Approval, Publication, and Activation

## Closed-world boundaries

This package authorizes no application/Python source change, runtime.env or
secret change, PostgreSQL or migration action, Docker Compose change, Storage
data or permission change, Telegram/Registry/Event/Core semantics, retry,
alternate process manager, second service/poller, reboot, n8n, Hermes,
OpenClaw, Brain, Memory, Specialist, or Stage 9.2.4 execution.

Stage 9.2.4 retains the full audit of secrets, database files, logs, backups,
and original business files. Only the narrow non-movement and non-regression
checks needed for Stage 9.2.3 are authorized here.

## Project Owner approval

I, as Project Owner, authorize one controlled Stage 9.2.3 production
source/runtime separation application on `aios-prod-01`.

Authorized mutations are limited to:

- creation of `/opt/aios/runtime/cache/pycache`;
- owner/group `aiosadmin:aiosadmin`;
- mode `0750`;
- preservation of the currently installed service artifact;
- one controlled service stop;
- reversible quarantine of independently verified generated source bytecode
  only;
- installation of the exact approved Stage 9.2.3 `aios.service`;
- daemon reload;
- one controlled service start; and
- source/runtime separation verification.

Exactly one polling process must exist after completion. No reboot, database
mutation, source-code change, runtime.env change, Docker change, Storage
change, or application semantic change is authorized.

`PROJECT OWNER APPROVAL = APPROVED`

## Publication and activation

- Branch: `governance/stage-9.2.3-controlled-vps-separation-approval`
- Baseline: `9579083000a675a264ce482eaf7323df5840e111`
- Allowed diff: governance records in this directory only
- Production mutation before activation: `PROHIBITED`
- Activation: normal merge of the dedicated governance PR

Pre-merge review must prove governance-only scope, exact artifact identity,
closed-world production authority, complete stop/rollback rules, no secret
content, and a clean/mergeable PR.

Post-merge audit must prove `HEAD == main == origin/main`, a clean worktree,
this approval package present, unchanged service/test artifacts, and no VPS
mutation during the approval workflow.

After successful merge and audit:

`STAGE 9.2.3 VPS SEPARATION APPROVED — READY FOR CONTROLLED EXECUTION`
