# Project Owner Approval, Publication, and Activation

## Project Owner approval

I, as Project Owner, approve Stage 9.2.3 repository implementation limited to:

- adding
  `Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`;
- adding `ReadOnlyPaths=/opt/aios-src`; and
- updating the focused systemd service test.

No other service, runtime, configuration, application, database, Docker,
Storage, or production behavior change is authorized.

The exact future repository paths are:

1. `deploy/systemd/aios.service`
2. `tests/unit/core_platform/test_aios_systemd_service.py`

Approval does not itself implement either change or grant VPS authority.

## Publication and activation

- Branch: `governance/stage-9.2.3-implementation-approval`
- Baseline: `9da47009e7f7b92f1022c6daf2b4393fd48d7263`
- Publication scope: governance records in this directory only
- Activation: normal merge of the dedicated governance PR

Pre-merge review must prove governance-only scope, exact authority, no service
or test delta, unchanged service blob
`ace763735417d196f3841fb526d76b4e593fbbc3`, and a clean/mergeable PR.

Post-merge audit must prove `HEAD == main == origin/main`, a clean worktree,
this package on `main`, governance-only merge scope, unchanged service and test
artifacts, and no VPS/production mutation.

After successful normal merge and audit, the next official action is:

`Stage 9.2.3 repository implementation`

Only then may the two authorized repository paths change.

`STAGE 9.2.3 IMPLEMENTATION APPROVED — READY TO BUILD`
