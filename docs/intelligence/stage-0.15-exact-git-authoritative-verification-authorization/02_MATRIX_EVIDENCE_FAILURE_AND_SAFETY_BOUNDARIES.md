# Matrix, Evidence, Failure, and Safety Boundaries

The future controlled execution is authorized for exactly these non-live gates:

1. Stage 0.15 integration test;
2. CoreToBrainMapper tests;
3. BrainInput tests;
4. BrainSemanticReceiver tests;
5. BrainInferenceInvoker tests;
6. Ollama adapter mock tests;
7. inference contract tests;
8. Core regressions;
9. Domain regressions;
10. Stage 8 gates;
11. Stage 9 gates;
12. full repository suite;
13. compile/static;
14. dependency/import audit;
15. prohibited-source audit;
16. `git diff --check`; and
17. exact Stage 0.15 one-path audit.

The raw evidence directory must retain exact source and blob identities, clean
status, Python/pip/pytest versions, `pip freeze`, requirements source SHA,
commands, stdout/stderr, exit codes, timestamps, counts, skip reasons, each gate
classification, and the final classification. Raw execution evidence must not
be edited and must contain no secrets or business content.

Source mismatch, acquisition or installation failure, unexpected tooling,
collection failure, or any required gate failure requires an immediate stop
with evidence retained. Source edits, pytest changes, added packages, modified-
environment retries, failure-to-skip conversion, and repository patching are
prohibited. Historical counts are comparison-only; fresh results control.

No mutation is authorized for `/opt/aios-src`, the production venv,
`aios.service`, PostgreSQL, Telegram, Ollama, Docker production state, firewall,
runtime services, production secrets, or production/business data. Model load
and inference are prohibited. No cleanup is authorized until final closure and
separate cleanup authority.
