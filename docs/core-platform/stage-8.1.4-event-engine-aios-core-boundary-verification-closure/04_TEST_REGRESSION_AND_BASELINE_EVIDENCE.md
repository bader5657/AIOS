# Test, Regression, and Baseline Evidence

Accepted pre-merge evidence included 10 focused Stage 8.1.4 passes and 10 Stage
8.1.3 passes with zero skipped. The legacy Registry-to-Event regression retained
Registry commit-before-Event visibility, exact envelope mapping, record-id
exclusion, failure preservation, no retry, and transaction-boundary assertions
while adding the active Core requirement only to its successful path.

Post-merge critical verification produced 66 passed and 36 subtests passed,
covering focused Stage 8.1.4, Stage 8.1.3, Registry-to-Event, Universal
Ingestion, Stage 6 Event Engine, and Stage 7 AIOS Core evidence. The monolithic
suite produced 406 passed and 696 subtests passed.

The eleven capability-matrix subfailures reproduced the exact accepted
environment/test-isolation baseline. They are pre-existing, unchanged,
unrelated, and non-blocking for Stage 8.1.4. They are not fixed or waived by
this closure.

Compile/static checks passed. Dependency audit reported no broken requirements.
Prohibited-source and clean-worktree audits passed. Disposable PostgreSQL was
used only for authorized regression evidence and removed afterward; no
production database or application network was used.
