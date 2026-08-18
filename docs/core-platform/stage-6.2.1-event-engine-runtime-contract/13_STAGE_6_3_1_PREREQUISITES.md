# Stage 6.3.1 Implementation Prerequisites

Before any Event Engine runtime code may be authorized or written:

1. this Stage 6.2.1 package must be merged, active, and closed;
2. Stage 6.2.2 Domain Foundation separation audit must be accepted/closed;
3. an exact Stage 6.3.1 baseline must be resolved from Git;
4. a separate implementation approval must close exact runtime/test paths;
5. that approval must preserve the two-file runtime preference unless concrete
   evidence justifies a named scope expansion;
6. async handler/result/error APIs and invariants in this package must be
   translated without semantic additions;
7. dependency, prohibited-source, historical-restoration, no-broker,
   no-persistence, and closed-world test gates must be specified; and
8. Stage 6.3.2 publisher integration, AIOS Core consumers, and all later work
   must remain excluded.

Stage 6.3.1 is the implementation stage, but this package itself grants no
build authority. “Ready for implementation approval workflow” means only that
the contract exists; approval cannot become effective before Stage 6.2.2.
