# Verification Requirements and Rollback Principle

Future implementation approval must require at minimum:

1. an exact baseline and closed runtime/test path list;
2. no historical cherry-pick or restoration;
3. no historical state module or six-state enum;
4. Request Context and recognized identity supplied upstream;
5. no reclassification inside Asset Pipeline;
6. applicable Store Original before Metadata;
7. Metadata before Document Manifest;
8. success only after every applicable boundary succeeds;
9. deterministic failure without false readiness;
10. originals preserved across downstream failure;
11. all ten approved input classes preserved;
12. accepted single-file, multi-file, Text, and URL-only behavior preserved;
13. no URL/network retrieval;
14. current storage paths, metadata semantics, and Manifest schema preserved;
15. no duplicate/idempotency semantics;
16. no Registry execution, Registry Entry, PostgreSQL, ORM, migration, or
    transaction behavior;
17. no canonical/domain Asset object;
18. no new general dependency direction;
19. Storage → App remains zero;
20. focused new pipeline and failure-boundary tests pass;
21. current Request Context and Stage 3 regressions pass;
22. full Core Platform and Domain Foundation regressions pass;
23. schema, compile/static, dependency, no-network, and Registry scans pass;
24. reviewer confirms no disguised historical state or semantic owner; and
25. closed-world diff contains only explicitly approved paths.

## Rollback Principle

Rollback the future code/test implementation if it restores prohibited
historical behavior, changes accepted Stage 2/3 semantics, requires an
unapproved path, introduces a new dependency, produces ambiguous success,
executes Registry/PostgreSQL behavior, or fails any mandatory gate.

Rollback is code/test only. This disposition record and Git history remain as
audit evidence; no production-data rollback or migration is involved.
