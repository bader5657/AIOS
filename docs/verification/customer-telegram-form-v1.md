# Customer Telegram Form v1 verification

Status: implementation and automated verification PASS; real Telegram form E2E pending.

- Baseline main after PR #325: `1cdd11c229a2409c72a0d68b4bc94d536b0eebaf`.
- Reviewed/tested application commit: `d945109b59129064d2f7d35db3e3d930c7dc138a`.
- [Automated disposable verification](https://github.com/bader5657/AIOS/actions/runs/38207371261): exit 0, 469 passed, 0 failed, 0 errors, 0 skipped.
- Counts: domain 219, application 52, adapter 20, Telegram boundary 15, Telegram authorization 136, PostgreSQL integration 27.
- New form specification was observed failing against baseline in [red run](https://github.com/bader5657/AIOS/actions/runs/38206935304). First implementation run exposed six exact API assertions requiring the approved optional phone extension; assertions updated, not removed.
- Independent source review of base..application commit: no actionable findings. Reviewer did not execute tests.
- [Prior JSON Telegram E2E evidence](https://github.com/bader5657/AIOS/blob/4b0fbb5f2b41c325fd75c981bee635d3552efbc4/docs/verification/telegram-e2e-20261012.md) is baseline evidence, not evidence that the new form passed.
- [New real form E2E run](https://github.com/bader5657/AIOS/actions/runs/38207496914) pins that tested application commit and harness `834ddb390cc3a49d67ff1d19ad52e108170507e1`. Pending live Owner interaction; no PASS claim yet.

## Scope and compatibility

`catat pelanggan` returns Nama, Alamat, Kota, No. Telp and Ket. Filled messages use one line per label. Name, address, city retain existing domain requirements; phone and notes are optional. Phone remains an exact string (leading zeros preserved), up to 64 characters, digits with optional leading + and formatting spaces/parentheses/hyphens. This is formatting validation, not phone reachability verification.

Migration 0008 adds nullable TEXT phone. Existing rows and old SQL inserts survive; new repository code requires migration 0008 first. Rollback drops phone values and requires an explicit administrative decision. No production migration was run.

Owner authorization, confirmation TTL and atomic customer/audit/consume mechanism remain. `batal pelanggan` invalidates pending confirmation. Telegram sends the confirmation command as its own copyable message. Old JSON commands and phone-absent snapshots remain compatible.

Automated coverage includes parsing, empty/invalid/duplicate fields, optional values, no write before confirmation, cancellation/stale messages, duplicate/reordered delivery, edited drafts, expiry, concurrent confirmation, revocation, forwarded messages, runtime privileges, audit rollback/immutability, restart retry, phone persistence and migration compatibility.

The live runner uses only the confirmed nonproduction bot username, repository secret by name, a fresh hash-verified challenge and disposable loopback PostgreSQL with a restricted runtime role. No token, raw numeric identity or confirmation token is logged. Container cleanup runs on success/failure. No merge or deployment authorized.
