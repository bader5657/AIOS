# Test, Baseline, and Static Evidence

Authority-relevant pre-merge evidence was reconfirmed and the critical gates
were rerun after merge on `118b9998c52a155cbd0a434e9b8f7188c6ffdf0a`.

| Gate | Result |
|---|---|
| Focused Stage 8.1.1 integration | 10 passed; 8 subtests in accepted evidence |
| Telegram input boundary | 15 passed |
| Combined focused/boundary authority gate | 25 passed; 58 subtests in accepted evidence |
| RequestContext | 6 passed |
| Universal Ingestion relevant | 31 passed; 57 subtests in accepted evidence |
| Asset/Storage accepted gate | 30 passed; 83 subtests; expanded post-merge rerun 37 passed |
| Core Platform relevant | 25 passed; 48 subtests |
| Domain Foundation | 212 passed; 454 subtests in accepted evidence |
| Stage 5 Registry | 11 passed; 27 environment-skipped |
| Stage 6 Event Engine | 15 passed |
| Stage 7 AIOS Core | 13 passed; 4 subtests in accepted evidence |
| Compile/static | PASS |
| Dependency audit / `pip check` | PASS; no broken requirements |
| Prohibited-source and reverse-dependency audit | PASS |
| Diff check and three-path closed world | PASS |

The monolithic pytest suite is not represented as fully green. On both clean
`main` baseline `d702f8c63c06b41794acba0255a9c51565686b2f` and the implementation
branch, it produces the same 11 capability-matrix subtest failures for Text,
Image, Voice, Audio, Video, PDF, DOC, DOCX, Spreadsheet, Web Link, and YouTube
Link. The exception fingerprint is unchanged: test-isolation leaves real
Storage/Registry environment behavior visible. Focused capability tests pass.

Disposition: **PRE-EXISTING BASELINE / NON-BLOCKING FOR STAGE 8.1.1**. There
are zero authority-relevant regressions.
