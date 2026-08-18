# Stage 3.5.1 Scoped Working Procedure

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Starting baseline | `ef55b65141773739360b3d5e942ef84c5603ce86` |
| Data policy | Synthetic temporary test data only; production data **NO TOUCH** |

1. Start a separate implementation branch from accepted `main` containing
   this activated package and record the exact branch baseline before edits.
2. Confirm a clean tree and read the active Stage 3.5.1 disposition and this
   entire package.
3. Modify only the six paths in `01_SCOPED_CHANGE_REQUEST.md`.
4. Keep `InputType` and recognition/classification ownership in App/Ingestion.
5. Pass `recognized_input_type.value` explicitly to Storage for the single-file
   path and `file_original_type.value` for each multi-file original.
6. Make Storage require the neutral string; remove its App import and fallback
   classification without moving App types or creating a replacement enum.
7. Preserve attachment selection, suffix/original filename, storage class,
   stored path, failure/cleanup behavior, and all lifecycle ordering.
8. Run every mandatory gate in `04_VERIFICATION_CONTRACT.md` and record exact
   commands, counts, results, diff, and implementation commit.
9. Stop on ambiguity, scope expansion, failed gate, or behavior drift.
10. Stop for Project Owner implementation acceptance. Do not deploy, migrate,
    execute Registry, access production data, or start Stage 4/5.
