# Acceptance Criteria

Stage 6.3.1 implementation later passes only if:

- the runtime is fresh, async, in-process, in-memory, sequential, and exactly
  conforms to Stage 6.2.1;
- all three and only three failure dispositions are implemented and tested;
- Domain Foundation tree and tests remain unchanged;
- Stage 6.2.2 dependency direction remains intact;
- handler order, snapshot, counts, invalid input, no-handler, and failure-stop
  behavior are proven;
- no deferred integration, retry, duplicate/idempotency, persistence, broker,
  network, AIOS Core, Brain, or Specialist semantics leak in;
- no new dependency or historical API returns; and
- exactly the four authorized files change and every verification gate passes.

Implementation completion does not itself close Stage 6.3.1 verification or
authorize Stage 6.3.2.
