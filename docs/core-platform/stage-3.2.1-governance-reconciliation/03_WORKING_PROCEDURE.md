# Stage 3.2.1 Working Procedure

| Control | Value |
|---|---|
| Lifecycle | **PROPOSED** |
| Accepted baseline | `0091561d26342e9551d1470c6014bb47cb015fc8` |
| Target branch | `main` |

1. Confirm this package is Approved, Published, Active, and accepted in `main`.
2. Confirm the implementation start is a governance-only descendant of the
   accepted baseline and contains no intervening source/test/runtime change.
3. Preserve unrelated working-tree material and modify only the seven allowed
   implementation/test files.
4. Use isolated synthetic temporary paths; never inspect runtime storage.
5. Implement only the active contract without architecture or authority work.
6. Stop Store Original failures before Metadata, Manifest, Registry, Event
   Engine, AIOS Core, Brain, and Specialists.
7. Execute the exact compilation, targeted tests, Core Platform regression,
   repository regression, `git diff --check`, and changed-file verification.
8. Stop for Project Owner review; do not commit, merge, deploy, or advance to a
   later stage as part of the implementation task.

This procedure authorizes no implementation until the final activation record
is accepted in `main`.
