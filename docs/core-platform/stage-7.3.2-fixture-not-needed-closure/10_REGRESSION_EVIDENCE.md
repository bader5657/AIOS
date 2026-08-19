# Regression Evidence

Unchanged evidence rerun on baseline
`30d2223c5d18716cc87e51a2f185c17ea24b50de`:

| Gate | Result |
|---|---|
| Focused AIOS Core | 13 passed |
| Domain Foundation focused | 41 passed |
| Full Domain regression | 212 passed |
| Stage 6 Event Engine | 15 passed |
| Stage 6 Registry to Event integration | 4 passed; zero skipped |
| Core Platform regression | 83 passed |
| Compile/static | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source audit | PASS |

The Registry-to-Event suite used fresh disposable PostgreSQL schemas through
the test-only URL. Its container was stopped and removed after the run.
