# Acceptance, Rollback, and Stop Conditions

Future implementation is acceptable only when the diff is confined to the
four authorized paths and every verification gate passes. Failure of any gate,
need for another path, Registry API incompatibility, schema/migration need, or
need to change Manifest/Pipeline contracts stops work before expansion.

The exact stop disposition for an additional runtime file is:

`STAGE 5.4.1 SCOPE EXPANSION REQUIRED`

Implementation rollback means reverting only the future Stage 5.4.1 code/test
diff. It must not delete stored originals, completed Manifests, or accepted
Stage 5.3 Registry work.
