# Verification and Regression Gates

Approval requires the focused test to pass without skips for mandatory evidence,
plus unchanged regression evidence for:

- Stage 8.1.1 and Stage 8.1.2;
- Stage 5 Registry unit, integration, migration, and isolation behavior;
- Stage 6 Event Engine unit tests and Registry-to-Event integration;
- relevant Universal Ingestion tests;
- relevant Asset Pipeline and Document Manifest tests;
- relevant Core Platform regression;
- full Domain regression;
- Stage 7 AIOS Core regression, without invoking Core in the focused test;
- compile/static checks;
- dependency and prohibited-source audits;
- `git diff --check`;
- exact one-file closed-world implementation diff.

Known baseline or environment failures must be reproduced and classified separately.
No Stage 8.1.3-relevant regression may be waived as baseline behavior.
