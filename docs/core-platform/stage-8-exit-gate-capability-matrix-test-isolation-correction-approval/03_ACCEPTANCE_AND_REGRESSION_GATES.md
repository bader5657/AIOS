# Acceptance and Regression Gates

The corrected test must pass:

1. in isolation;
2. after pre-importing the real Telegram Adapter;
3. after pre-importing Universal Ingestion and Registry; and
4. inside the complete Stage 8 Exit Gate cumulative suite.

It must leave no fake module state in later Universal Ingestion, Registry,
Telegram, or Stage 8 tests. Existing Stage 8.1.1–8.4.1, Stage 5/6/7, Core,
Domain, compile/static, dependency, prohibited-source, capability-matrix, and
`git diff --check` gates must pass with no mandatory failure.

The implementation diff must contain exactly the authorized test path. No
runtime correction is expected or authorized.
