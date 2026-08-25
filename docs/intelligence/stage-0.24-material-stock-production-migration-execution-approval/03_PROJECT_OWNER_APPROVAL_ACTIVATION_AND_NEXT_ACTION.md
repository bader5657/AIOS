# Project Owner Approval, Activation, and Next Action

I, as Project Owner, approve one future controlled production execution of the
exact verified `0002_create_material_stock.up.sql` migration.

The execution may create only the empty `material_stock` table under one
transaction after a clean source, exact migration-hash, healthy PostgreSQL, and
table-absence preflight.

No material rows, role/grant changes, retrieval, inference, Registry mutation,
service restart, or unrelated schema changes are authorized.

If the migration fails, stop and roll back the transaction. If
post-verification is inconsistent, do not repair automatically.

Publication is governance-only through a normal pull request into `main`,
without force push or history rewrite. This authority activates only after the
governance PR is merged and the future operator verifies a clean synchronized
`main`, the immutable migration identity, the exact production database
identity and health, transaction capability, no migration-identifier collision,
and table absence.

The next official action after activation is one controlled production
deployment session following this package. That session must retain the required
evidence and stop on any failed gate. It must not retry.

`STAGE 0.24 MATERIAL STOCK PRODUCTION MIGRATION EXECUTION APPROVED — READY FOR CONTROLLED DEPLOYMENT`
