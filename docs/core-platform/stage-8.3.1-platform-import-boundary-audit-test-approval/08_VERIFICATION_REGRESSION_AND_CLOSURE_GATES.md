# Verification, Regression, and Closure Gates

Required evidence includes:

- focused Stage 8.3.1 test passing with all prohibited reverse edges zero;
- accepted positive directions preserved without brittle assertions;
- zero Python import cycles;
- zero Brain runtime, Memory, Specialist Router, and concrete business imports from the official Stage 8 runtime;
- narrowly bounded Telegram SDK and Mission Status exceptions;
- no import-time external-state execution;
- optional dependency and type boundaries preserved;
- Stage 8.1–8.2, Stage 5/6/7 critical, Core, and Domain regressions passing;
- compile/static, dependency, prohibited-source, and `git diff --check` passing; and
- a closed-world diff containing exactly the authorized test file.

The known capability-matrix failures remain pre-existing, unchanged, unrelated,
and outside Stage 8.3.1 if reproduced identically. No database, production
execution, Telegram network, external application network, or new
infrastructure is required for the focused static audit.

After technical verification, a governance-only verification, architecture
review, acceptance, publication, activation, post-merge audit, and closure
package requires its own authorized documentation scope.
