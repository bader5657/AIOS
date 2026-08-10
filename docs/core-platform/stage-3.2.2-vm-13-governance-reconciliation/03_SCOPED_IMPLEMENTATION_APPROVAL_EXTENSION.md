# Stage 3.2.2 VM-13 Scoped Implementation Approval Extension

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Authority effect | **ACTIVE FOR VM-13 VERIFICATION ONLY** |
| Scope | Verification/governance correction only |

The requested approval authorizes the repository execution environment's
`python3` interpreter and Python standard-library `unittest` as the sole
official Stage 3.2.2 verification mechanism. It authorizes no implementation,
test rewrite, dependency installation, runtime execution, migration, or
production-data access.

Acceptance requires the corrected commands to execute the targeted four-module
suite, every Core Platform test module, and both repository unit-test domains;
all must pass after activation. Any nonzero exit, import/discovery error,
unexpected zero-test result, dependency demand, changed-file violation, or
authority contradiction means STOP.
