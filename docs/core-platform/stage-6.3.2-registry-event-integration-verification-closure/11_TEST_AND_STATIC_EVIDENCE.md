# Test and Static Evidence

Post-merge evidence on `5751fc9eaf2cf7bf7e83796e73163170fe7334e2`:

| Gate | Result |
|---|---|
| Stage 6.3.2 focused unit | 26 passed |
| Stage 6.3.2 disposable PostgreSQL integration | 4 passed; zero skipped |
| Complete Registry integration | 27 passed |
| Stage 5 Registry unit | 11 passed |
| Stage 6.3.1 Event Engine | 12 passed |
| Domain regression | 212 passed |
| Core Platform regression | 83 passed |
| Pipeline regression | 9 passed |
| Compile/AST | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source and reverse-dependency audits | PASS |
| Four-file merge-scope audit | PASS |

The sole review-loop defect was a test expecting `ValueError` instead of the
active Domain Foundation `DomainValidationError`; it was corrected before all
final gates passed.
