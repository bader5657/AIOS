# Regression and Verification Gates

Implementation acceptance requires:

- the focused Stage 8.1.4 test with zero mandatory skips;
- unchanged Stage 8.1.1–8.1.3 evidence;
- Stage 6 Event Engine regressions;
- Stage 7 AIOS Core regressions;
- relevant Universal Ingestion and lifecycle regressions;
- Core Platform relevant regression;
- full Domain regression;
- compile/static checks;
- dependency audit;
- prohibited-source and reviewer audits;
- `git diff --check`; and
- a closed-world diff containing exactly the authorized paths.

Review must confirm sole caller ownership, success-only gating, zero Core calls
on no-event/failure, same-envelope identity, one Core call, minimal result
projection, no Brain, no retry/dedupe, no cross-component transaction, and
upstream preservation.

Known unrelated baseline failures must be reproduced and classified separately;
no Stage 8.1.4-relevant failure may be waived.

Approval-baseline reconfirmation ran the current Event Engine, AIOS Core,
Universal Ingestion, and lifecycle suites: 54 tests and 46 subtests passed.
Compile/static and dependency checks passed. This governance workflow changed
no runtime or test file.
