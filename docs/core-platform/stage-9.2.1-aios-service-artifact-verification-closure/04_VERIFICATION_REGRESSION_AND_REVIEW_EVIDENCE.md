# Verification, Regression, and Review Evidence

The focused static test parses the real tracked unit and verifies its exact
sections, directive sets, values, one-ExecStart invariant, interpreter-only
preflight, required external environment, restart/shutdown/hardening policy,
single-process topology, and prohibited content.

Accepted evidence:

- focused Stage 9.2.1 test: `7 PASS + 53 subtests`, zero skipped;
- post-merge cumulative verification: `443 PASS + 763 subtests`, zero skipped;
- Stage 8 regressions: `PASS`;
- Core regression: `PASS`;
- Domain regression: `PASS`;
- compile/static: `PASS`;
- dependency audit: `PASS`.

Local `systemd-analyze verify` parsed the directives. Its only diagnostic was
the absence of the production interpreter/path under `/opt/aios/...` in the
local verification environment. This is an
`EXPECTED LOCAL ENVIRONMENT LIMITATION`, not a syntax or service-contract
defect, and production paths are not changed to satisfy a workstation.

Reviewer audit found no optional EnvironmentFile, wrong path, duplicate
ExecStart, shell wrapper, secret/test-DSN leakage, database/network preflight,
migration, Docker lifecycle ownership, retry loop, excess hardening,
containerization, or runtime change. The static test enforces exact allowed
section keys so later unauthorized directives fail deterministically.
