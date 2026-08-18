# Implementation Acceptance Criteria

Stage 5.3.1 implementation may be accepted only when:

1. exact Psycopg dependency is the only dependency change;
2. exact migration matches Stage 5.2.1;
3. original-binary exclusion passes;
4. only persistence-local DTOs exist;
5. register/read/update contracts pass and delete is absent;
6. SQL is parameterized;
7. one-operation transaction and READ COMMITTED boundaries are preserved;
8. rollback occurs on persistence error without Storage/Manifest effect;
9. no automatic retry exists;
10. isolated execution uses only the test DSN;
11. migration apply/down/re-apply and schema inspection pass;
12. all unit/integration/static/regression gates pass;
13. Stage 3/4 and Stage 5.1/5.2 authority remain unchanged;
14. Stage 5.4.1 integration is absent; and
15. the closed-world path audit passes.

Passing Stage 5.3.1 does not close Stage 5.3.2 or Stage 5.
