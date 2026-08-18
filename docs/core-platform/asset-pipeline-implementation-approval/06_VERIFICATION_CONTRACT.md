# Mandatory Verification Gates

Implementation may be accepted only when all gates pass:

1. Request Context is constructed upstream and accepted correctly;
2. all ten approved input/media classes remain supported;
3. file-backed single-file flow is preserved;
4. Text flow is preserved;
5. Web Link flow is preserved with exact URL and no retrieval;
6. YouTube Link flow is preserved with exact URL and no retrieval;
7. Store Original ordering is preserved;
8. Metadata ordering is preserved;
9. Document Manifest ordering is preserved;
10. storage failure is contained;
11. metadata failure is contained;
12. Document Manifest failure is contained;
13. success is possible only after Manifest success;
14. Registry execution remains absent;
15. PostgreSQL/ORM/migration dependency remains absent;
16. network retrieval remains absent;
17. no persistent Pipeline state machine exists;
18. no historical/equivalent six-state enum exists;
19. no canonical/domain Asset object exists;
20. dependency-direction and import audit passes, including Storage → App zero;
21. all accepted Stage 3 storage, metadata, Manifest, lifecycle, capability,
    single-file, multi-file, and failure regressions pass;
22. full relevant Core Platform suite passes;
23. Domain Foundation regression suite passes;
24. compile/static and schema meta-validation pass; and
25. closed-world diff contains exactly and only authorized paths.

Additional required review checks:

- no historical patch was copied wholesale;
- Pipeline delegates instead of recreating Stage 3 logic;
- recognition remains upstream;
- result is runtime transport only;
- duplicate/retry/transaction behavior is absent; and
- Registry/PostgreSQL/no-network source scans are clear.
