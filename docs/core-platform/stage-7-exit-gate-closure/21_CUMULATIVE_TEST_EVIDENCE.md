# Cumulative Test Evidence

Unchanged cumulative evidence rerun on closure baseline
`4f78ac9b04a947db0825ae09d612484bc91d53ee`:

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
| Repository cleanliness and diff check | PASS |

The Registry-to-Event regression used fresh disposable PostgreSQL schemas via
the test-only URL. Its container was stopped and removed after the run. No
production database or test file was changed.
