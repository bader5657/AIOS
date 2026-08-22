# Authority, Exact Baseline, and Milestone Boundary

## Exact baseline resolution

The pre-branch repository check established:

| Ref | SHA |
|---|---|
| `HEAD` | `05d65805d1970f0de4c7957fbad02e386a0770fe` |
| `main` | `05d65805d1970f0de4c7957fbad02e386a0770fe` |
| `origin/main` | `05d65805d1970f0de4c7957fbad02e386a0770fe` |

The worktree was clean. The SHA is the normal merge of PR #104, the Stage 9
Exit Gate final closure. It is the exact Stage 10 completion-verification
baseline and must remain the subject of Stage 10.1–10.3 evidence.

## Controlling authority

Authority is read in this order:

1. `docs/AIOS_ARCHITECTURE_v1.md` (Blueprint);
2. `docs/AIOS_Roadmap_Frozen.md`;
3. `docs/core-platform/CORE_PLATFORM_EXECUTION_PLAN_v1.md`;
4. accepted Stage 5 registry closure packages, Stage 6/7/8 exit-gate closure
   packages, and Stage 9 accepted closure packages;
5. `docs/core-platform/stage-9-exit-gate-final-closure/` and merge PR #104;
6. the Project Owner Stage 10 evaluation recorded in this package;
7. root `VERSION`;
8. active `docs/governance/GOVERNANCE_DECISION_005.md` version authority;
9. accepted requirement/capability/completion matrices in Stages 1–9;
10. `docs/governance/GOVERNANCE_DECISION_004.md` and
    `docs/reviews/AIOS_RELEASE_REVIEW_v0.4.md` for release-governance precedent.

Old branches and historical implementations are evidence provenance only.
They are not current authority and cannot replace current `main`.

## Exact boundary

“Stage 10 completion” in this workflow means completion of the approved Core
Platform milestone: the Blueprint platform path through AIOS Core and its
explicitly connected support and operational requirements. It never means
completion of the full AIOS product or any later phase.

Stage 10.4.1, 10.4.2, 10.5.1 execution, 10.6.1, the Stage 10 final exit gate,
release execution, and Intelligence-stage work are outside this authority.
