# Test and Static Evidence

Post-merge evidence on `ceac8b4ff41b7967b63bd7861b692a1bea0e8527`:

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
| Four-file implementation merge-scope audit | PASS |

The Registry-to-Event integration evidence used a fresh disposable
`postgres:17-alpine` container, unique schemas, and the test-only
`AIOS_REGISTRY_TEST_DATABASE_URL`. The container was stopped and removed after
the successful run.
