# Migration Execution Evidence Contract

Against an explicitly authorized isolated test/development PostgreSQL only,
future evidence must prove:

1. fresh up migration succeeds;
2. exact table, columns, types, nullability, constraints, primary key, and
   identity behavior exist;
3. no binary type/column, unauthorized uniqueness/index, or foreign key exists;
4. down migration reverses an empty/disposable schema;
5. re-apply after reversal succeeds; and
6. no valued or production data is involved.

Direct application of the SQL files is approved for evidence. No migration
framework is required or authorized.
