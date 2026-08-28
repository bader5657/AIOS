# Stage 0.33B-P Canonical Bundle, Target, and Activation Binding

## Immutable canonical-bundle binding

This authority does not create or reproduce SQL. It binds exclusively to the
existing merged authoritative document:

`docs/intelligence/stage-0.33b-read-only-production-preflight-authorization/01_READ_ONLY_QUERY_AND_EVIDENCE_CONTRACT.md`

Publication hashes are:

| Bound artifact | Required SHA-256 |
|---|---|
| Entire authoritative query-contract document | `b2d360deba9a588ac4ea617ef71f5d0ec0f2cb2a04991f7b173cae48d55e9687` |
| Extracted canonical executable SQL bundle bytes | `64435ab0193ceb454569496f954a9c6788355f035834d7a6b095222b5154d6f3` |

Future execution must mechanically extract that document's single canonical
bundle and verify both hashes before production connection. Missing, additional,
duplicate, reordered, rewritten, or substituted SQL is prohibited.

The exact sequence is P01-P05, I01-I02, M01-M02, S01, Z01, F01-F04, O01-O08,
R01-R04, C01. The canonical SQL remains byte-for-byte unchanged.

All existing protections remain controlling: one bundle; `BEGIN READ ONLY`;
canonical `SET LOCAL` only; target identity first; exact physical order; no
arbitrary or exploratory SELECT; no runtime addition; no psql meta-command; no
side-effect or user-defined function execution; no dynamic SQL; no DDL, DML,
lock, GRANT, REVOKE, COPY, DO, CALL, EXECUTE, or PREPARE; closed safe-function
allowlist; evidence minimization; and stdout-only bounded evidence.

## Frozen target and corrected I02 interpretation

The frozen control plane and target remain:

```text
/usr/bin/docker exec -i aios-postgres /usr/local/bin/psql
    -X -v ON_ERROR_STOP=1 -U aios -d aios
```

SQL is stdin-only. Host PostgreSQL, DSN, alternate endpoint/container/database/
user, argument substitution, or fallback is prohibited.

I02 SQL is unchanged. PASS requires exactly database `aios` owned by `aios`,
schema `public` owned by `pg_database_owner`, relation `material_receipts` of
kind `r` owned by `aios`, with session user `aios` and PostgreSQL major 17.
Every I02 value must be retained; any deviation is BLOCKED/STOP without repair.

## Full proof starts from zero

No missing proof is inherited from PR `#244` or `#245`. The new session must
independently execute and pass:

- M01-M02: creator column and named creator CHECK absent;
- S01: Stage 0.32 active-source index present, valid, ready, unique, sole-keyed
  by `source_asset_reference`, with unchanged predicate;
- Z01: exact unfiltered `COUNT(*)` on `public.material_receipts` equals zero;
- F01-F04: fresh four-table canonical counts and digests;
- O01-O08: fresh structural/security/object snapshot; and
- R01-R04: fresh role attributes, membership, ADMIN OPTION, ACL/table privilege,
  and column-privilege snapshot.

Zero-row eligibility and Migration 0005 pre-state are currently UNKNOWN/NOT
RECONFIRMED. Diagnostic D01/D02 does not substitute for any full-preflight step.
Migration 0004 must not run.

## Immediate activation conditions

Immediately before production connection, all conditions must pass:

1. this authorization PR received independent review PASS with zero blockers;
2. it was merged unchanged and Project Owner approval remains applicable;
3. `HEAD == main == origin/main` and the worktree is clean;
4. the reviewed authorization head/merge commit/current main are recorded and
   authorization content is unchanged;
5. the authoritative query-contract document and canonical-bundle hashes match;
6. both Migration 0005 hashes match;
7. the frozen target and exact control-plane argv are unchanged; and
8. no newer governance revoked or incompatibly superseded this authority.

Any failure before connection means DO NOT CONNECT, STOP, and authority remains
unconsumed. No automatic pull, merge, rebase, reset, clean, stash, repair,
container/image replacement, restart, argument substitution, alternate target,
or fallback is authorized.

