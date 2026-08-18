# Stage 3.3 Scoped Working Procedure

| Control | Value |
|---|---|
| Lifecycle | **PUBLISHED AND ACTIVE** |
| Starting baseline | `3167ca3f2a0eefbd109f984f696b7cd58665a62a` |
| Data policy | Synthetic temporary files and values only; production data **NO TOUCH** |

1. Start a separate implementation task and branch from the exact accepted
   Activation baseline containing this package.
2. Confirm Stage 3.3.1 and this package are Published and Active in accepted
   `main` history, with a clean tree and exact ancestry.
3. Modify only the two allowed source files and four allowed test files.
4. Preserve `Store Original → Extract Metadata → Create Manifest → Register`.
5. Preserve the Stage 3.2.2 mixed/multiple-original endpoint: aggregate storage
   readiness only, with no Metadata or later progression.
6. Implement the required metadata fields and only locally deterministic,
   source-derived optional fields. Omit unavailable optional fields.
7. Do not fetch URLs, render, interpret content, enrich, guess, convert,
   transcode, mutate originals, or depend on Manifest during extraction.
8. Run every gate in `04_VERIFICATION_CONTRACT.md` and record exact evidence.
9. Stop for Project Owner implementation review. Do not deploy, migrate,
   activate services, access production data, or begin Stage 3.4.
