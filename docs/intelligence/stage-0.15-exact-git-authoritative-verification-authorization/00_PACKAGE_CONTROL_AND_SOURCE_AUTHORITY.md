# AIOS Intelligence Stage 0.15 — Exact Git-Authoritative Verification Authorization

| Control | Approved value |
|---|---|
| Work type | `GOVERNANCE / AUTHORIZATION ONLY` |
| Authority baseline | `62e768c167a98b15eda35c83e4a687e55d0c3e9c` |
| Implementation PR | `#163` |
| Exact source SHA | `21aeed1ad0f87a3a28835a9aaf4b67a0f8fab44f` |
| Merge SHA | `4a692a58e516520f7cb10cb3315eb348e7b5b34d` |
| Implementation path | `tests/integration/test_core_to_brain_chain.py` |
| Implementation/merge blob | `435a4205cce7f64a51da41a6673c6bff9e0d5f96` — identical |
| Decision | `APPROVED — READY FOR CONTROLLED ENVIRONMENT PREPARATION` |

At review start, `HEAD`, `main`, and `origin/main` were identical at the clean
authority baseline. Git and PR #163 independently resolve the exact source SHA.
The prior `...f8cab44f` value is superseded as a documentation error; the
corrected character is `f`.

Before preparation, the isolated checkout must be detached and clean, and
`git rev-parse HEAD` must equal the exact source SHA byte-for-byte. Any mismatch
aborts the operation. Moving `main`, an abbreviated SHA, or the merge SHA may
not substitute for the authorized source.
