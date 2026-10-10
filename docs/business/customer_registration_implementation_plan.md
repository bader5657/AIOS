# Minimum Customer Registration implementation plan

Approved scope: minimum_business_authorization_p1.md; base 49bd2316.

1. Add failing policy tests for identity, expiry, draft replacement, retry,
   rollback and Telegram transport admission.
2. Implement narrow CustomerRegistration orchestration with existing Draft,
   Application and Customer; inject one PostgreSQL unit of work.
3. Add migration 0007 for singleton enrollment, confirmations and append-only
   audit; administrative bootstrap remains separate from runtime credentials.
4. Add opt-in Telegram adapter integration and preserve ordinary ingestion.
5. Add disposable database tests for real commits, concurrency, rollback,
   privilege rejection, audit immutability and collision protection.
6. Run unit/security regression checks and exact-head disposable verification.
   Record unavailable tests as NOT_RUN, never PASS.
7. Independently review, fix within scope, verify exact diff and create PR.
   No merge, production migration, deployment or activation.
