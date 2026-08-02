# Core Platform Stage 1.2.2 Registry Disposition

## Record

| Field | Value |
|---|---|
| Execution Plan position | Stage 1 — Main Step 1.2 — Sub Step 1.2.2 |
| Current review baseline | `3307ea0113ea5b567882149436865c114f626299` (`main`) |
| Historical component commit | `d58c1c341e6a27dd40de63baf004505fcc3094e2` |
| Historical commit subject | `feat(core-platform): add registry foundation` |
| Historical branch evidence | `origin/sprint-18-conversation-engine` |
| Review method | Read-only source, test, dependency, persistence, and authority comparison |
| Component disposition | **REJECT** |
| Review date | `2026-08-02` |

The historical commit is not an ancestor of current `main` and is not current
implementation. This disposition rejects it as a PostgreSQL Registry
implementation; it does not delete the historical evidence or prevent later
authorized work from considering individual field concepts.

## Scope

This review covers only the Registry files introduced by commit `d58c1c3`:

| Historical path | Role |
|---|---|
| `core/registry/__init__.py` | Package marker |
| `core/registry/models.py` | Four-field `RegistryRecord` dataclass |
| `core/registry/registry.py` | `Registry.save()` pass-through method |
| `tests/unit/registry/__init__.py` | Test package marker |
| `tests/unit/registry/test_registry.py` | One pass-through equality test |

Asset Pipeline, Event Engine, AIOS Core, and all later component reviews are
excluded.

## Current Authority Used for Comparison

The active Blueprint provides the following Registry constraints:

- PostgreSQL Registry follows Document Manifest and precedes AIOS Event Engine
  in the official pipeline;
- Register is an explicit ingestion lifecycle step after Create Manifest;
- original files are not stored as the primary binary in PostgreSQL; and
- PostgreSQL stores identity, metadata, relationships, status, and file
  location.

The frozen Execution Plan reserves schema, migration, transaction, CRUD scope,
database isolation, failure behavior, and integration decisions for Stage 5.
No approved Stage 5 data responsibility or persistence contract is present at
the current review baseline. This review therefore does not invent a database
model, driver, ORM, transaction policy, or Registry API.

## Evidence Comparison

| Historical behavior | Authority/current-baseline comparison | Finding |
|---|---|---|
| `RegistryRecord` contains `id`, `media_type`, `storage_path`, and `manifest_path` | Identity and file-location concepts overlap part of the Blueprint responsibility | Partial field evidence only; not an approved data contract |
| Record omits general metadata, relationships, and status | Does not cover the complete responsibility explicitly assigned to PostgreSQL | Incomplete |
| `Registry.save()` immediately returns its input | Performs no registration or persistence | Reject as Registry implementation |
| No PostgreSQL connection, query, driver, transaction, schema, or migration exists | Cannot implement the named PostgreSQL Registry boundary | Reject |
| No original binary field exists | Does not contradict the binary-outside-PostgreSQL rule | Narrowly aligned, but insufficient |
| One test asserts returned record equality | Proves only pass-through behavior, not persistence, isolation, failure, or lifecycle registration | Insufficient verification |
| Test is a pytest-style function | No pytest dependency is pinned in the historical or current `requirements.txt` | Cannot be adopted blindly |
| PostgreSQL Compose asset exists | Infrastructure is unchanged between historical and current baselines, but historical Registry does not use it | No application integration evidence |

A case-insensitive static search across the historical Registry source, test,
and dependency manifest found no PostgreSQL, database-driver, connection,
query, commit, rollback, transaction, cursor, or execute reference. The
historical and current `requirements.txt`, PostgreSQL Compose configuration,
deployment script, and ingestion manifest configuration are identical.

## Disposition

**REJECT** the historical `core/registry/` component as an implementation of
the Blueprint PostgreSQL Registry.

Reasons:

- it does not persist or register data;
- it implements only a subset of the explicitly required data responsibility;
- it has no PostgreSQL application dependency or integration;
- it establishes no approved persistence or transaction boundary; and
- its single test verifies a no-op return rather than Registry behavior.

The names `id`, `media_type`, `storage_path`, and `manifest_path` remain
historical evidence only. They are not accepted as field names, schema, API,
or contract through this disposition.

Any future Registry implementation remains dependent on the verified Document
Manifest output and the approved Stage 5.1 data responsibility and Stage 5.2
persistence contracts. Resolving those dependencies now would exceed Sub Step
1.2.2, so none is implemented here.

## Validation and Result

Review evidence was obtained with read-only Git inspection of commit metadata,
the complete historical patch, all five historical files, current authority,
current-tree absence, branch containment, database-related symbols,
dependencies, PostgreSQL infrastructure, and current baseline inventory.

No historical file was copied or merged. No source, test, dependency, schema,
database, runtime, authority, milestone, freeze, or product-status artifact was
changed.

**Sub Step 1.2.2 result: PASS**

Main Step 1.2 remains in progress. The next frozen-plan position is Stage 1,
Main Step 1.2, Sub Step 1.2.3. That Sub Step is not started by this disposition.
