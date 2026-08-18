# Test and Static Evidence

Post-merge evidence on `814d937cfa1eeea0af12d3a1d2c3c5226ce3011e`:

| Gate | Result |
|---|---|
| Focused Event Engine | 12 passed |
| Domain Foundation focused | 74 passed; 77 subtests passed |
| Full Domain regression | 212 passed; 454 subtests passed |
| Core Platform regression | 77 passed; 169 subtests passed |
| Compile/static | PASS |
| Dependency audit | PASS; no broken requirements |
| Prohibited-source audit | PASS |
| Reverse-dependency audit | PASS |
| Four-file merge-scope audit | PASS |

The three pre-existing Domain test collection warnings do not represent failed
tests and were outside authorized scope.
