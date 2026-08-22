# Publication, Activation, and Next Official Action

## Governance publication

- Branch: `governance/stage-9.3.1-capability-claims-correction-approval`
- Baseline: `5dc7e504240a168b5acf466be1e23efd9b6f9b1d`
- Scope: files in this governance package only
- Activation: normal merge of a clean, mergeable governance PR to `main`

Pre-merge review must prove a governance-only diff, all approval decisions,
the exact two-path future scope, no protected content, and no README,
CHANGELOG, authority, implementation, version, release, or production change.

Post-merge audit must prove `HEAD == main == origin/main`, a clean worktree,
the complete package on `main`, unchanged `README.md` and `CHANGELOG.md`, no
implementation/runtime change, and no VPS access or mutation.

## Activation result

Normal merge and successful post-merge audit activate this authority for the
declared two-file future implementation scope only.

## Next official action

After activation, the next eligible action is:

`Stage 9.3.1 README/CHANGELOG capability-claims implementation`

That work must use a separate branch and PR and may edit only the two approved
documentation paths. This package does not begin the implementation.
