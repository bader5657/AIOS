# Review, Implementation, and Closure Sequence

The mandatory sequence is:

1. merge this exact-baseline test approval;
2. activate Project Owner approval;
3. implement only the authorized test file;
4. run focused and regression verification;
5. review and normally merge the test-only PR;
6. rerun post-merge verification;
7. record Project Owner acceptance;
8. publish and activate the Stage 6.4.1 governance closure; and
9. perform a separate read-only Stage 6 exit-gate evaluation.

The implementation branch must not force-push, bypass checks, rewrite history,
or merge a runtime change.
