# ORM, Driver, and Runtime Deferral

Stage 5.2.1 selects no ORM or PostgreSQL driver and installs no dependency.
SQLAlchemy, psycopg, asyncpg, and every other client remain unauthorized until
a separate implementation/dependency approval before Stage 5.3.1.

The approved schema must remain understandable in plain SQL regardless of a
future implementation choice.

No final `register`, `read`, `update`, or `delete` API is defined. Read/update
semantics, runtime types, packages, error surface, connection management, and
query behavior are deferred to separately approved Stage 5.3.1 work.
