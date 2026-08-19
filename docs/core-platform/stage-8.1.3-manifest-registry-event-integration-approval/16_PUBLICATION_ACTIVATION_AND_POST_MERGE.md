# Publication, Activation, and Post-Merge Contract

Publication occurs through the dedicated governance-only pull request containing
this package. Activation occurs only when that PR is normally reviewed and merged
into `main` without bypassing required checks.

After merge, the merge commit becomes the exact implementation baseline. The
implementation workflow must verify synchronized `HEAD`, `main`, and `origin/main`,
a clean worktree, and that no runtime or test implementation entered main through
this approval PR.

The active outcome is:

`STAGE 8.1.3 INTEGRATION/TEST APPROVED — READY TO VERIFY`

This activation does not implement Stage 8.1.3, authorize runtime correction, or
begin Stage 8.1.4.
