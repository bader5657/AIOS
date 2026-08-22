# Project Owner Approval, Publication, and Activation

## Project Owner approval

I, as Project Owner, approve a narrow Stage 9.2.3 production
source-deployment alignment correction.

The current running service must remain untouched while Git objects and target
authority are prepared. The actual `/opt/aios-src` checkout may change only
during the controlled zero-poller cutover window.

The deployed revision must contain the exact already-approved Stage 9.2.3
service artifact and no additional unauthorized runtime implementation.

No application semantic, database, configuration, Docker, Storage, or
business-data change is authorized.

`PROJECT OWNER APPROVAL = APPROVED`

## Publication and activation

- Branch:
  `governance/stage-9.2.3-production-source-deployment-alignment-approval`
- Baseline: `fe1b748ee48dddd6f01e45214e1f9a23d9724267`
- Allowed diff: governance records in this directory only
- VPS access or mutation during approval workflow: `PROHIBITED`
- Activation: normal merge of the dedicated governance PR

Pre-merge review must prove the exact target ancestry and artifact identities,
governance-only diff, complete preparation and zero-poller boundaries, source
integrity stop rule, rollback compatibility, no secrets, and a clean mergeable
PR.

Post-merge audit must prove `HEAD == main == origin/main`, a clean worktree,
this package present, implementation/service/test artifacts unchanged by this
approval, and no VPS mutation during the governance workflow.

After normal merge and successful post-merge audit:

`STAGE 9.2.3 SOURCE DEPLOYMENT ALIGNMENT APPROVED — READY TO RESUME CONTROLLED EXECUTION`
