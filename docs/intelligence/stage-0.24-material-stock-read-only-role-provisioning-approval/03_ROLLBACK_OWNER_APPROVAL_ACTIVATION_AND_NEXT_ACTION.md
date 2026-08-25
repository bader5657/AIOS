# Rollback, Project Owner Approval, Activation, and Next Action

If future provisioning is incorrect, separately controlled rollback may revoke
only the exact table, schema, and database grants; remove any unexpected
membership if separately authorized; and drop the dedicated role only after
catalog inspection proves it owns nothing and has no production dependency.
This approval does not execute rollback.

I, as Project Owner, approve a dedicated least-privilege PostgreSQL authority for
Stage 0.24 material-stock retrieval.

The future retrieval identity may connect only to the AIOS database, use the
required schema, and SELECT only from `public.material_stock`.

It must not receive business-write, DDL, role-management, ownership,
unrelated-table, or Brain-visible credential privileges.

Role provisioning does not authorize data population, retrieval execution,
inference, Universal Ingestion, or Level C.

Publication is governance-only through a normal pull request into `main`,
without force or history rewrite. No production role or privilege is changed
during publication.

After merge and fresh clean-main/production preflight, the next official action
is exactly one controlled role-provisioning session implementing only the frozen
role posture and three minimum grants, followed by read-only validation.

`STAGE 0.24 MATERIAL STOCK READ-ONLY ROLE PROVISIONING APPROVED — READY FOR CONTROLLED ROLE CREATION`
