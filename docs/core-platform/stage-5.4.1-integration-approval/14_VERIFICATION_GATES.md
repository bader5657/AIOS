# Required Verification Gates

Implementation acceptance requires all gates below on one exact candidate:

1. Universal Ingestion is the sole Registry caller.
2. No Pipeline → Registry dependency exists.
3. No Document Manifest → Registry dependency exists.
4. Register occurs only after completed Manifest and true readiness.
5. One ready lifecycle produces exactly one Register call.
6. Storage failure produces zero calls.
7. Metadata failure produces zero calls.
8. Manifest failure produces zero calls.
9. `identity_ref` equals the exact Manifest path.
10. `manifest_ref` equals the exact Manifest path.
11. Represented media type is unchanged.
12. Metadata is unchanged.
13. Relationships equals `[]`.
14. Registration status is `None`.
15. File-backed storage path is exact.
16. Text storage path and source URL are `None`.
17. URL source is exact and storage path is `None`.
18. No URL retrieval or normalization occurs.
19. Disposable PostgreSQL contains the successful row.
20. Success result contains `registration_succeeded=True` and returned record ID.
21. Registry failure produces false success and no record ID.
22. Registry failure preserves original, metadata, and completed Manifest.
23. No cross-component rollback occurs.
24. No retry or duplicate call occurs.
25. Registry transaction remains internal.
26. No Registry runtime, schema, or migration changes occur.
27. Stage 5.3.x Registry regressions pass.
28. Stage 3/4 regressions pass.
29. Core Platform regressions pass.
30. Pipeline regressions pass.
31. Domain regressions pass.
32. Compile, static dependency, and closed-world diff audits pass.
