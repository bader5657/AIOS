# Stage 3.2.2 VM-13 Scoped Governance Change Request

| Control | Value |
|---|---|
| Lifecycle | **DRAFT** |
| Baseline | `0845dc4f836b3fafff5a9c66a346b5ca098863ab` |
| Requested change | Revalidate and authorize standard-library `unittest` for VM-13 |

## Allowed Targets

1. `docs/core-platform/stage-3.2.2-authority-extension-package/05_MINIMUM_CONTRACT_VERIFICATION.md`
2. This reconciliation package.

Every other target is forbidden. In particular, this request does not change
Blueprint, Frozen Roadmap, Execution Plan, Authority Hierarchy, Canonical
Model, Layer Architecture, ADR, Pipeline Model, runtime architecture, storage
behavior, implementation source, tests, configuration, or dependencies.

Replace the VM-13 mandatory pytest commands with executable repository-aware
Python standard-library `unittest` commands. Define the official interpreter,
runner, targeted suite, Core Platform suite, full repository/domain regression,
failure behavior, and evidence requirements. Preserve VM-01 through VM-12 and
VM-14 exactly.

Stop on test incompatibility, dependency demand, scope growth, authority gap,
zero-test discovery, failed command, or attempt to change source/tests merely
to make the runner pass.
