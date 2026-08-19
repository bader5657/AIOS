# Verification and Regression Gates

Implementation is acceptable only when all gates pass:

1. exact focused integration test contract;
2. RequestContext constructed once, solely inside Universal Ingestion;
3. unchanged Message/text delegation and preserved command separation;
4. correct bounded acknowledgement/non-success matrix;
5. Storage-only download/original persistence with no duplicate download;
6. no retry, media-group state, link fetch, real network, infrastructure, or
   production change;
7. Request Context unit tests unchanged;
8. Universal Ingestion unit and lifecycle/capability tests unchanged;
9. Asset Pipeline, Telegram input/storage, and relevant Core Platform tests;
10. Domain Foundation regression;
11. Stage 5 Registry, Stage 6 Event Engine, and Stage 7 AIOS Core critical
    regressions required by repository acceptance;
12. Python compile/static checks;
13. dependency-direction audit and prohibited-source audit;
14. `git diff --check`;
15. closed-world implementation diff limited exactly to the authorized paths.

No mandatory gate may be skipped. Fake-only tests must make later boundaries
deterministic and must not claim Stage 8.1.2–8.4.1 completion.
