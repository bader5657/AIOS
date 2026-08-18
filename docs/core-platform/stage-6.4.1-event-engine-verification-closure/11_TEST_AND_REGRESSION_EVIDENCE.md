# Test and Regression Evidence

Pre-merge and post-merge evidence on the test implementation:

| Gate | Result |
|---|---|
| Focused/full Event Engine | 15 passed; zero skipped |
| Registry unit | 11 passed |
| Domain Foundation focused | 63 passed |
| Full Domain regression | 212 passed |
| Core Platform regression | 83 passed |
| Pipeline regression | 9 passed |
| Full Registry integration/isolation/failure/migration | 27 passed |
| Stage 6.3.2 focused integration within that suite | 4 passed; zero skipped |
| Compile/AST | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source/reverse-dependency | PASS |
| Diff check and one-file closed world | PASS |

Database tests used fresh unique disposable schemas and were not skipped.
