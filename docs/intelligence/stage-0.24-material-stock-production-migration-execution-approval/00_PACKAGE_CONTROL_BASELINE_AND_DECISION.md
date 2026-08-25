# AIOS Intelligence Stage 0.24 — Production Migration Execution Approval

| Control | Approved value |
|---|---|
| Approval source baseline | `5f6814fee835578e3ddc6d3b7adfece273c058f5` |
| Source state at evaluation | `HEAD == main == origin/main`; clean after `git fetch origin main` |
| Implementation status | `VERIFIED — ACCEPTED — CLOSED` |
| Up migration | `migrations/postgres/0002_create_material_stock.up.sql` |
| Up migration SHA-256 | `a6d4a7be98fe8ecb6914a6231f9d2ddcd76e2ec7fb30a87759d8ba6be9320d5f` |
| Down migration | `migrations/postgres/0002_create_material_stock.down.sql` |
| Down migration SHA-256 | `045dc369c3b0a7174463bdb80a9b1831666f8827a857226da52a9ec670e9b0c3` |
| Decision | one future controlled production execution approved |
| Execution during publication | `PROHIBITED` |
| Maximum DDL result | one empty `material_stock` table |

The immutable execution identity is the exact up-migration path and SHA-256 at
the approval source baseline. Future execution must begin from a clean,
synchronized `main` and reproduce that exact hash. A changed file hash,
different path, divergent source, or dirty worktree invalidates activation and
requires a return to governance.

This package is governance and execution approval only. Publication performs no
database connection, migration, production mutation, role provisioning, data
population, retrieval, inference, Registry mutation, Universal Ingestion
wiring, or service restart.

The repository contains no persistent migration-history table or migration
framework. Repository inspection found only ordered SQL migration files. The
future operator must not invent a history mechanism. Activation therefore uses
the immutable file identity, the production catalog collision check, and the
strict table-absence gate.
