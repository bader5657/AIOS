# Stage 3.4.1 Scoped Working Procedure

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Starting baseline | `773fc37d01e5205138d91a325fd510c975b80862` |
| Data policy | Synthetic temporary test data only; production data **NO TOUCH** |

1. Begin a separate implementation branch from an accepted `main` containing
   this activated package; record the exact branch baseline before edits.
2. Confirm the Stage 3.4.1 authority and this approval are Published and Active,
   and that the starting tree is clean.
3. Modify only the seven exact paths in `01_SCOPED_CHANGE_REQUEST.md`.
4. Preserve `Store Original → Extract Metadata → Create Manifest → Register`;
   implementation ends at successful Manifest output/register readiness and
   must not execute Register.
5. Reconcile the runtime producer and schema together. Do not treat the current
   example JSON as authority during the change.
6. Pass the already-successful bounded Stage 3.3 metadata into Create Manifest;
   do not re-extract, reinterpret, mutate, enrich, or add metadata fields.
7. Preserve exact stored-original bytes and exact received URLs. Use no remote
   access and no production data.
8. Make artifact completion safe: validate before completion and use the
   simplest local atomic write/replace or equivalent bounded mechanism so a
   failure leaves no valid-looking completed artifact.
9. Run every mandatory gate in `04_VERIFICATION_CONTRACT.md`; record commands,
   counts, results, exact diff, and implementation commit.
10. Stop for Project Owner implementation acceptance. Do not deploy, migrate,
    activate services, implement Registry, or start Stage 3.5.
