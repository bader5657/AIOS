# Database, Test, and Regression Evidence

Database execution used `AIOS_REGISTRY_TEST_DATABASE_URL` only, pointing to a
dedicated disposable PostgreSQL 17 container with explicit test credentials.
Every test used a unique schema, applied the existing migration unchanged, and
dropped its schema during cleanup. The container was stopped and removed after
verification. No production URL, credential, database, or fallback was used.

Accepted pre-merge and post-merge evidence:

| Gate | Result |
|---|---|
| Focused Stage 8.1.3 | 10 passed; zero skipped |
| Post-merge focused Stage 8.1.3 | 10 passed; zero skipped |
| Stage 8.1.1 + Stage 8.1.2 integration | 16 passed |
| Stage 5 Registry unit/integration/migration/isolation/failure | 38 passed |
| Stage 6 Event Engine + Registry→Event | 19 passed |
| Universal Ingestion | PASS |
| Asset Pipeline and Document Manifest | PASS |
| Core Platform relevant regression | PASS |
| Domain Foundation regression | PASS |
| Stage 7 AIOS Core | PASS |
| Critical post-merge matrix | 343 passed; 593 subtests passed |
| Compile/static | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source/diff audit | PASS |
| Closed-world verification diff | PASS; exactly one test path |

Governance-closure reconfirmation at baseline `dc83a1c` produced 10 focused
passes with zero skips, 53 combined Stage 5/Stage 6 passes, and 290 relevant
Core/Domain/AIOS Core passes with 560 subtests. Compile/static and dependency
checks passed again. This reconfirmation changed no runtime or test file.

The monolithic suite produced 396 passed and 691 subtests passed while retaining
exactly the known 11 capability-matrix subfailures. Their fingerprint matches
the previously recorded test-isolation/environment baseline. They are
**PRE-EXISTING BASELINE / UNCHANGED / UNRELATED / NON-BLOCKING FOR STAGE
8.1.3**. They were not fixed, waived, or added to Stage 8.1.3 scope.
