# Stage 0.33B-P Fresh Full Preflight Authority Basis

Date: 2026-08-28 (Asia/Jakarta)

## Publication boundary

This package is authorization documentation only. Publication does not contact
production PostgreSQL, execute a SELECT or preflight, run Migration 0005 or
0004, perform DDL, DML, locks, ownership or role/grant changes, modify runtime
or integrations, restart a service/container, or activate candidate traffic.

## Corrected governance basis

Stage 0.33B target-identity governance correction PR `#246` was independently
reviewed, merged, and verified at merge commit
`1038b64841868d8d4112ec6e15e6504d0d177fed`. The exact target-specific,
fail-closed identity is:

| Field | Required value |
|---|---|
| Database | `aios` |
| Database owner | `aios` |
| Session user | `aios` |
| Schema | `public` |
| Schema owner | `pg_database_owner` |
| Relation | `public.material_receipts` |
| Relation kind | `r` |
| Relation owner | `aios` |

Any other tuple is BLOCKED and returns to governance. This package authorizes no
ownership repair, normalization, `SET ROLE`, membership, ACL, GRANT, or REVOKE
involving `pg_database_owner` or any other role.

## Consumed history and new authority identity

The full-preflight authority from PR `#244` is permanently consumed. Its
historical result remains BLOCKED under the then-current governance expectation;
Stage 0.33B-PD later proved that expectation defective. The diagnostic authority
from PR `#245` is also permanently consumed. Neither authority is revived,
renewed, replaced, extended, or reusable.

This package creates one distinct future Stage 0.33B-P authority. After every
activation condition in this package passes, it permits exactly one new bounded
READ-ONLY production preflight session starting from zero current eligibility
evidence. It does not authorize a session by publication or before merge.

## Source and immutable migration artifacts

Publication was based on clean synchronized
`HEAD == main == origin/main == 1038b64841868d8d4112ec6e15e6504d0d177fed`.
The recalculated Migration 0005 hashes are:

| Artifact | Required SHA-256 |
|---|---|
| UP | `7de76e82cb26863cd3c14abc4394cb036936ed0f1c6c64819f03094cf9069293` |
| DOWN | `c210305a14399b4826abc46fad75c138bc8e698d9b85380eba893a01c1501b16` |

Migration 0005 is not executed or authorized. Migration 0004 must not rerun.

## Project Owner approval

The Project Owner approves exactly one NEW future full Stage 0.33B-P READ-ONLY
production preflight session using the corrected exact owner tuple and unchanged
canonical query bundle, subject to all activation conditions.

The Project Owner does not authorize reuse of PR `#244` or PR `#245`, Migration
0005 or 0004, DDL, DML, locks, ownership changes, role/grant/membership changes,
repair, retry, runtime/service or integration changes, or candidate activation.
