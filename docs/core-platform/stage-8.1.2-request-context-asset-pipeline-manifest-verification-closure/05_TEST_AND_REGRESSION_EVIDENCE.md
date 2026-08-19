# Test and Regression Evidence

Pre-merge and post-merge required evidence:

| Gate | Result |
|---|---|
| Focused Stage 8.1.2 | 6 passed; zero skipped |
| Asset Pipeline | 9 passed |
| Universal Ingestion + lifecycle | 26 passed |
| Document Manifest + RequestContext | 20 passed |
| Stage 8.1.1 integration | 10 passed |
| Combined critical Stage 2–4/8.1.1 | 65 passed post-merge |
| Core Platform | 83 passed |
| Domain Foundation | 212 passed |
| Stage 5 Registry unit | 11 passed |
| Stage 5 database integration | 27 environment-skipped; no database requested by this stage |
| Stage 6 Event Engine | 15 passed |
| Stage 7 AIOS Core | 13 passed |
| Compile/static | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source/diff audit | PASS |
| Closed-world implementation diff | PASS; exactly one test path |

The monolithic pytest suite retains exactly the known 11 capability-matrix
subfailures: 359 passed, 27 environment-skipped, and 655 subtests passed on the
implementation branch. Their fingerprint matches the previously reproduced
clean-main test-isolation/environment baseline and is **PRE-EXISTING BASELINE /
NON-BLOCKING FOR STAGE 8.1.2**. No Stage 8.1.2-relevant regression exists.
