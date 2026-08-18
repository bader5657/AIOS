# Scope and Terminology Decision

## Closed Scope

Stage 5.1.1 governs only structured registration information in five
categories: identity, metadata, relationships, status, and file
location/reference. Category names are responsibility boundaries, not fields,
objects, payloads, tables, columns, or APIs.

## Terminology

| Term | Disposition |
|---|---|
| `PostgreSQL Registry` | Canonical Stage 5 capability name established by the Blueprint and Canonical Model |
| `Registry` | Permitted shorthand inside Stage 5 governance only after unambiguous reference to `PostgreSQL Registry` |
| Blueprint Brain-consumable `Registry` | Not interpreted, redefined, or equated by this package |
| `Registry Entry` | Remains **UNRESOLVED** and is not created |

The shorthand is editorial and scope-bound. It does not resolve the Canonical
Model's repository-wide equivalence question, create two Registry concepts,
or amend architecture. Where ambiguity is possible, the full canonical name
`PostgreSQL Registry` is mandatory.

## Contract Character

This is a responsibility contract only. It is not a domain model, Registry
Entry contract, runtime interface, persistence model, database design, schema,
migration, transaction contract, or implementation approval.
