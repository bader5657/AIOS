# Cumulative Test Evidence

Evidence executed on exit baseline `cad232760fb5fd1b9ea2186b8e7d4be51fad748a`:

| Gate | Result |
|---|---|
| Event Engine Stage 6.3.1/6.4.1 | 15 passed |
| Registry unit | 11 passed |
| Domain Foundation focused | 63 passed |
| Full Domain regression | 212 passed |
| Core Platform regression | 83 passed |
| Pipeline regression | 9 passed |
| Full Registry integration/isolation/failure/migration | 27 passed |
| Stage 6.3.2 integration within that suite | 4 passed; zero skipped |
| Compile/AST | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source/reverse-dependency | PASS |
| Diff check and repository cleanliness | PASS |

Database evidence used fresh unique disposable schemas only through
`AIOS_REGISTRY_TEST_DATABASE_URL`; production database access was prohibited.
