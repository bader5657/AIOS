# Down Content Review and Corrected Hash Freeze

The authoritative down artifact is:

`migrations/postgres/0003_create_material_receipt_inventory_movement.down.sql`

Its only executable effects are dependency-ordered drops of:

1. `inventory_movements`;
2. `material_receipt_items`;
3. `material_receipts`.

The production target schema is `public`; as with the repository migration
convention, unqualified names resolve through the separately verified target
search path. The artifact contains no `CASCADE`, material-stock or registry
operation, unrelated-object operation, role or grant logic, data insert/update,
runtime action, or production execution mechanism. Its leading comment states
that destructive production reversal is unauthorized.

The content matches the frozen Stage 0.27 rollback contract. No implementation
review, file edit, migration replacement, or new test is required.

The corrected immutable package identity is frozen as:

| Artifact | SHA-256 |
|---|---|
| `0003_create_material_receipt_inventory_movement.up.sql` | `e858f5ad210aca2d7e6a2badf3dab2585cf33eacdcf46e6b6bf839dcea7d37eb` |
| `0003_create_material_receipt_inventory_movement.down.sql` | `c374837cad14df82126ab56ae487766694911ed89cbdace1382faeb40aebb8fe` |

The down hash identifies repository rollback tooling only. Normal production
down execution remains unauthorized.
