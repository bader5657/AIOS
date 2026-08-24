# New Session Authority, Project Owner Acceptance, and Activation

After this governance package is merged and clean `main` is synchronized, one
new first Session-Bound Level B v1 execution attempt is authorized. It must:

- generate a new session ID and exclusive-create a new journal;
- use exactly one Stage 0.19 composition and one client/provider lifecycle;
- admit exactly the following two fixed synthetic requests, with no third:
  1. `Temperature stable and vibration within normal range.`
  2. `System pressure is stable and motor temperature remains within normal range.`
- start request 2 at least 60 seconds after request 1 starts, only after request
  1 completes successfully and all spacing and safety gates pass;
- use concurrency `1`, queue `1`, no retry, no fallback, and timeout
  `120000 ms/request`;
- remain within 30 minutes, with this attempt capped at exactly 2 requests and
  the general Level B ceiling remaining 5; and
- finalize the journal and stop after request 2 or the first failure.

Previous evidence and journals remain immutable. No prior session ID or journal
may be reused. Only one temporary `/tmp` harness and one new exclusive session
journal are authorized as future operational artifacts. No network, firewall,
service, source, or runtime mutation is authorized.

Real user data and business data are prohibited. Universal Ingestion remains
inactive. Production activation and Level C are prohibited.

## Project Owner acceptance

I, as Project Owner, accept the operator-completed privileged read-only network
preflight evidence as the Stage 0.21 session-level privileged network gate,
provided its file identity and contents verify exactly.

The next first-session execution harness must not attempt sudo again.

It may rely on the accepted privileged evidence together with fresh
non-privileged drift checks immediately before session creation and before each
admitted request.

A new execution attempt requires a new session ID and new exclusive journal and
remains limited to exactly two fixed synthetic requests under the existing
Stage 0.21 fail-closed controls.

No third request, second session, real data, production activation, Level C,
retry, fallback, or runtime/network mutation is authorized.

Publication requires a normal governance-only PR into `main`, without force or
history rewrite. Publication executes no operational phase. Following merge
and a synchronized clean-main audit, activation is:

`STAGE 0.21 OPERATOR PRIVILEGED PREFLIGHT ACCEPTED — READY FOR NEW TWO-REQUEST SESSION EXECUTION`

The next official action is one separate operator-controlled execution task.
It must verify the accepted evidence identity and complete all fresh
non-privileged pre-session drift gates before creating the new session.
