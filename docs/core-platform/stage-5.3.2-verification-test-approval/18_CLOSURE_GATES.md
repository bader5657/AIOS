# Verification and Closure Gates

Stage 5.3.2 may close only when:

1. both and only the authorized test files change;
2. every required matrix scenario passes against the exact baseline;
3. integration tests execute on a proven disposable PostgreSQL and do not skip;
4. actual `READ COMMITTED`, commit visibility, rollback invisibility, and
   transaction independence pass;
5. failure paths raise the approved Registry-local error and do not retry;
6. original-file, Manifest, and binary containment pass;
7. schema/runtime/dependencies remain unchanged;
8. Stage 5.3.1 and Core/Pipeline/Domain regressions pass;
9. production access and Stage 5.4.1 wiring remain absent;
10. disposable database resources are cleaned;
11. reviewer authority and closed-world audits pass; and
12. normal commit, PR, review, and merge policy is followed.

No passing result defines same-row conflict or lost-update policy.
