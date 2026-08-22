# Preparation Boundary and Rollback Evidence

## Active-service preparation boundary

While `aios.service` remains active, only non-worktree-mutating Git operations
may be performed in `/opt/aios-src`:

- record branch or detached-HEAD state and exact HEAD;
- record configured remotes;
- record tracked and staged diffs separately;
- inventory all untracked and ignored residue without content disclosure;
- fetch required objects from the existing `origin` remote;
- inspect commits, ancestry, trees, and blobs; and
- calculate and compare artifact hashes from Git objects.

Checkout, reset, merge, source editing, tracked-file mutation, service restart,
and any operation that changes the active worktree are prohibited while the
service is running.

## Mandatory predecessor record

Before stop, preserve an execution record containing:

- current production source SHA
  `4168e098612c930215a49028d4ca9fc200d21cfd`;
- branch name or detached state;
- remote names and URLs;
- tracked diff;
- staged diff; and
- exact generated-residue inventory.

The current service artifact must also remain recorded as blob
`ace763735417d196f3841fb526d76b4e593fbbc3` and SHA-256
`50a603a236a88fd0527149e622ea1af203d94df6199318d0b64d1d45c1354c0e`.

This approval accepts the supplied verified VPS state as its operational
finding; it does not independently connect to or inspect the VPS.
