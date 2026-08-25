# Reauthorization Eligibility, Transaction, and Scope

The prior execution authority is consumed and must never be reused. This review
does not itself authorize a second execution. It finds the unchanged migration
eligible for a separate, fresh execution-authority decision after publication
of the corrected verifier contract.

A future authority must retain exactly one attempt and no retry:

1. complete clean-main, immutable-hash, production-identity, health, collision,
   and table-absence preflight;
2. `BEGIN`;
3. execute the exact verified up migration;
4. execute the corrected structured, explicitly typed read-only verification;
5. `COMMIT` only if every check passes;
6. otherwise `ROLLBACK`, stop, and retain evidence.

No production migration-file change or repository implementation change is
required. The failed verifier was temporary operator-side SQL and has no
existing governed script path to patch. The corrected contract is frozen in
this governance package. If a persistent verification harness is later desired,
its exact repository path and implementation require separate scope authority.

This review authorizes no migration rerun, down migration, schema repair, role or
grant, data insertion, Registry mutation, retrieval, inference, Docker/network
change, or service restart.

The remaining gate is a separate fresh execution-authority publication. That
authority must bind the immutable migration identity, this corrected verifier
contract, one new attempt, and the full production preflight. Eligibility is not
activation and is not permission to execute.
