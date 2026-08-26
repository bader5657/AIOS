# Review, Merge, and Next Authority

## Required sequence

1. Publish this Stage 0.29 documentation-only governance closure.
2. Review and merge its governance PR.
3. Verify `HEAD == main == origin/main` and a clean worktree.
4. Issue a separate repository implementation authority.
5. Create a separate implementation branch.
6. Implement only the approved Python and test paths.
7. Run focused unit tests.
8. Run disposable PostgreSQL integration and security-boundary tests.
9. Run relevant regression/full-suite and static-scope audits.
10. Obtain independent reviewer audit and merge only when clean.
11. Perform no production activation.

The implementation authority must not be inferred from this document before
the explicit post-merge authority is issued. It must not expand into Telegram,
OCR/Vision, inference, production data, production stock, runtime service,
systemd, runtime environment, or production role/grant work.

Telegram is already an existing AIOS integration concern. A later receipt
integration must extend that connection through the reviewed candidate and
confirmation APIs; it must not repeat basic setup without an observed defect.

## Governance disposition

The approved boundary is narrow, compatible with the existing architecture,
and has no remaining architecture or business-policy blocker. The next official
action after clean governance merge is issuance of repository implementation
authority for the enumerated packages and tests.

`INTELLIGENCE STAGE 0.29 MATERIAL RECEIPT CANDIDATE + POSTING IMPLEMENTATION GOVERNANCE APPROVED — READY FOR REPOSITORY IMPLEMENTATION AUTHORIZATION`
