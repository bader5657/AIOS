# Mandatory Future Implementation Verification

Stage 5.2.2 closure does not prove code, migration, schema, or database behavior
that does not yet exist. Every later Stage 5.3.x/5.4.x artifact must be
re-verified against this policy.

At minimum future evidence must prove:

1. no binary column or PostgreSQL binary type exists;
2. no original body is serialized into text or JSONB;
3. no base64 original content is persisted;
4. metadata contains only Stage 3.3.1-approved structured values;
5. Manifest remains reference-only;
6. file/source values remain references;
7. Storage ownership is preserved on success, failure, and rollback;
8. Registry persists only the five approved structured categories; and
9. migration/schema/runtime diffs remain traceable to the Active design.

Failure of any gate blocks implementation acceptance and the Stage 5 exit
gate. This obligation grants no implementation authority.
