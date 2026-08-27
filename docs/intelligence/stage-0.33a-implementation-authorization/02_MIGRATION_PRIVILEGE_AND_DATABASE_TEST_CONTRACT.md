# Migration, Privilege, and Database Test Contract

## Migration-number gate

At publication, repository inventory ends at Migration 0004, so the expected next number is `0005`. Before implementation begins, inventory must be checked again. If `0005` is occupied, stop and return to governance; do not rename or freeze another number without recording the drift.

## Migration 0005 UP

The authorized `UP` change is limited to `public.material_receipts`:

```text
ADD created_by_actor_reference TEXT NOT NULL
```

It must also add an explicitly named PostgreSQL `CHECK` enforcing all of:

- exact ASCII `operator:` prefix;
- valid UUID syntax;
- canonical lowercase UUID text;
- canonical hyphenation; and
- UUID version nibble `4`.

A superficial regex accepting arbitrary UUID versions, uppercase text, malformed syntax, noncanonical forms, or arbitrary operator IDs is prohibited. Application validation cannot substitute for the database contract. If exact enforcement proves impractical, stop, document the limitation, and return to governance before implementation merge.

No index, default, nullable transition, backfill, fabricated creator, new timestamp, provenance table, trigger, function, or unrelated schema change is authorized.

The implementation may be designed for the governed zero-row production path, but it must not contact production. Production row-count proof belongs only to separately authorized Stage 0.33B.

## Migration 0005 DOWN

The matching `DOWN` file may exist only for disposable PostgreSQL lifecycle and development/test rollback proof. It must reverse only the Stage 0.33A column/constraint and exact grant delta, following repository conventions.

Production `DOWN` is not authorized. There is no automatic rollback, post-commit fallback that destroys provenance, or generic rollback authority. Production removal after provenance-bearing rows exist requires separate destructive rollback governance.

## Exact candidate grant delta

The current candidate role has column-scoped receipt `INSERT`. The only authorized privilege addition is candidate-role `INSERT` on `created_by_actor_reference`, sufficient for legitimate candidate creation.

The implementation must not grant candidate or login identities:

- `UPDATE` on `created_by_actor_reference`;
- generic table or provenance update/delete authority;
- unrelated receipt/item insert authority;
- posting, inventory movement, or stock authority;
- schema/database ownership or object creation;
- DDL, administration, role creation, or grant option; or
- direct runtime-login ACLs outside the existing governed membership model.

The posting writer/runtime must not gain `UPDATE` or any mutation authority on creator provenance. Reader authority remains read-only. Roles, memberships, ownership, and unrelated ACLs remain unchanged except the exact candidate column-`INSERT` delta.

The allowed bootstrap-helper edit only mirrors this exact matrix for future governed provisioning/verification. It does not authorize executing the helper, rotating secrets, or changing production grants.

## Disposable PostgreSQL admission

All database proof must reuse the existing fail-closed disposable mechanism with:

- explicit `AIOS_MATERIAL_DISPOSABLE_TESTS=1` opt-in;
- numeric loopback `127.0.0.1`;
- a non-production dynamic port, never `5432`;
- an isolated governed test-database name;
- disposable credentials distinct from governed runtime credentials;
- no production fallback; and
- unconditional schema/role/database cleanup.

Production PostgreSQL is prohibited.

## Migration and schema matrix

Real disposable PostgreSQL tests are mandatory for:

- Migration 0005 `UP` on the approved empty baseline;
- exact `TEXT` type and `NOT NULL` posture;
- named `CHECK` existence and exact semantics;
- absence of an unapproved index;
- disposable-only `DOWN`;
- `UP → DOWN → UP` where appropriate;
- object/schema preservation; and
- the exact grant delta and its reversal according to repository convention.

Actual PostgreSQL must accept:

- `operator:<valid-lowercase-canonical-uuidv4>`.

It must reject:

- uppercase UUIDv4;
- UUIDv1;
- UUIDv3 where constructible;
- UUIDv5;
- the zero UUID;
- malformed UUID;
- missing-hyphen UUID;
- braced UUID;
- leading or trailing whitespace;
- `reviewer:<valid-uuidv4>`;
- `system:<valid-uuidv4>`;
- blank text; and
- `NULL`.

These tests must exercise PostgreSQL constraints, not only application validation. Database `CHECK` failure does not define the public application taxonomy; actor errors must be classified at the application/trust boundary before mutation wherever required.

## Privilege matrix

Using production-equivalent disposable roles, tests must prove:

- candidate can perform a legitimate receipt/items/creator insert;
- candidate can insert only the frozen candidate columns;
- candidate cannot update, erase, or rewrite creator provenance;
- candidate cannot perform unrelated insert/update/delete;
- candidate cannot post or mutate movements/stock;
- candidate has no admin, DDL, ownership, membership, or grant-option authority;
- posting cannot update creator provenance;
- reader remains read-only;
- runtime logins have no unintended direct ACLs; and
- ownership, memberships, and ACLs remain exact except the approved candidate `INSERT` delta.

## Atomicity and lifecycle database proof

Normal multi-item creation must atomically commit one receipt, its items, and its creator. A forced failure after receipt insertion or during item persistence must prove:

```text
receipt rows committed = 0
item rows committed = 0
provenance committed = 0
```

Revision, confirmation, rejection, cancellation, and posting must preserve the original creator before/after. Rejected and cancelled originals retain their creator. A legitimate replacement receives its own newly authenticated creator without copying or inheritance.

## Stage 0.32 and preservation proof

Migration 0005 and implementation must leave unchanged:

- Migration 0004 files and deployment state;
- `material_receipts_source_asset_active_uidx`, its uniqueness, and predicate;
- `SOURCE_ACTIVE_RECEIPT_EXISTS` behavior;
- existing indexes, unrelated columns, triggers, and functions;
- roles, ownership, memberships, and unrelated ACLs; and
- unrelated business data.

Creator identity is not a deduplication key. Same source by another valid actor yields `SOURCE_ACTIVE_RECEIPT_EXISTS`, creates no second active receipt, mutates no creator, and discloses no existing creator.
