# Regression and Verification Gates

After focused tests, acceptance requires:

- full Stage 6.3.1 Event Engine unit suite;
- unchanged Stage 6.3.2 Registry→Event Engine integration suite;
- required Stage 5 Registry unit/integration/isolation/failure/migration suites;
- Domain Foundation focused tests and full Domain regression;
- Core Platform regression;
- Pipeline regression;
- compile/static and dependency audits;
- prohibited-source and reverse-dependency audits;
- `git diff --check`; and
- closed-world diff containing exactly the one authorized test path.

Mandatory database evidence must not be skipped. Production remains untouched.
