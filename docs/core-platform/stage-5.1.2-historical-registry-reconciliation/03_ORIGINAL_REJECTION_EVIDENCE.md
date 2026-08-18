# Original Rejection Evidence

The Active Stage 1.2.2 record rejected the historical component as a
PostgreSQL Registry implementation. The exact proven deficiencies remain:

- `Registry.save()` is a pass-through and performs no registration or
  persistence;
- the four-field record does not cover the complete responsibility categories;
- no general metadata contract exists;
- relationships are absent;
- status responsibility is absent;
- PostgreSQL connection, query, dependency, driver, schema, and migration
  behavior are absent;
- no persistence or transaction boundary exists;
- no Document Manifest-to-Register lifecycle integration exists;
- no actual registration semantics exist; and
- the single equality test proves only pass-through identity.

The historical source contains no PostgreSQL, connection, cursor, query,
execute, commit, rollback, transaction, or persistence behavior. These are
observed absences, not invitations to design them in Stage 5.1.2.

The original component-level disposition was **REJECT**. No new repository
fact or Active authority invalidates its evidence.
