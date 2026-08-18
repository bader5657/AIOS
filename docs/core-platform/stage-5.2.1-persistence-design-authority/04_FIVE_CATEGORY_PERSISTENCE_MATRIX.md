# Five-Category Persistence Matrix

| Category | Approved persistence concept | Semantic owner/limit | Initial representation |
|---|---|---|---|
| Identity | Approved upstream identity/reference and represented media/input identity | Upstream values are not generated or reclassified | Required text values |
| Metadata | Snapshot of already-approved Stage 3.3.1 metadata | Stage 3.3.1 retains semantic authority | Required JSONB object |
| Relationships | Already-approved bounded relationship values only | No new vocabulary, cardinality, or business relationship | Required JSONB array, empty array permitted |
| Status | Already-approved registration status/disposition when available | No enum or transition authority | Nullable text |
| File location/reference | Storage reference, applicable exact source URL, and completed Manifest reference | Storage/Manifest ownership unchanged; reference only | Nullable/required text as specified |

No sixth responsibility category is introduced. Request Context may contribute
only a separately approved identifier in later authority; it is not a new
category and gains no column here.
