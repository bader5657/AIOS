# Customer Telegram Form v1 implementation plan

Approved design: user approved adding Kota and continuing on 2026-10-12.
Baseline: main after PR #325, 1cdd11c229a2409c72a0d68b4bc94d536b0eebaf.
Use executing-plans inline; one final independent code review. No merge or production changes.

- [ ] Add tests that fail for the missing form, cancellation and phone behavior.
- [ ] Add a nullable phone TEXT migration (0008), preserving existing rows and call signatures.
- [ ] Extend Customer, creation event, Draft, Application and repository with optional string phone.
- [ ] Add a narrow label parser: Nama, Alamat, Kota required; No. Telp and Ket optional.
- [ ] Route catat pelanggan, the filled form and batal pelanggan through current Owner transaction.
- [ ] Preserve old JSON command, 600-second confirmation, audit atomicity and idempotency.
- [ ] Validate legacy and new persistence, cancellation, invalid replacement, authorization and audit using disposable PostgreSQL.
- [ ] Review exact diff, then run real Telegram E2E on AIOSTesting_bot with new verified challenge.
- [ ] Save redacted evidence and open one PR to main. Do not merge.

Rulings:
- Isolate in a new remote feature branch. This projectless workspace has no Git checkout; connector commits and hosted exact-SHA checks are used, as in the prior successful milestone.
- Migration must precede use of new repository code. Old code remains compatible with the added nullable column.
- Blank optional form fields map to None. Strip layout whitespace around form values; preserve legacy JSON semantics.
- Phone is optional text preserving + and leading zeros, with a permissive display-format check (digits, initial +, spaces, parentheses, hyphens; maximum 64 characters), not a claim of number ownership or reachability.
- Start/cancel use current singleton lock and message ordering; older repeated commands must not invalidate a newer pending confirmation.
- A form is a self-contained message; no new conversation/form framework or process-local authority cache.
- Negative automated cases are reported separately from live Telegram transport cases.
