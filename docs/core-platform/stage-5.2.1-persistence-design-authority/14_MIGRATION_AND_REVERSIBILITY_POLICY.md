# Migration and Reversibility Policy

## Migration Approach

Use explicit, versioned, reviewable SQL migrations. Every future migration must
state its forward effect, prerequisites, exact baseline, verification method,
and reversibility assessment.

This package creates no migration file and authorizes no execution. Schema
changes require later implementation approval before an artifact is created or
run.

## Reversibility

Initial Registry schema creation should be structurally reversible in
development and staging. Where production data could be lost, rollback must
prefer application rollback or a forward corrective migration over destructive
database reversal.

No DROP, data deletion, production rollback, or production database operation
is authorized here.
