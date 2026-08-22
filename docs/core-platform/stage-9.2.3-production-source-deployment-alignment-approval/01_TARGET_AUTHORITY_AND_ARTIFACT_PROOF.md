# Target Authority and Artifact Proof

## Exact minimal authoritative revision

The approved production deployment revision is:

`2c44dc84cb38dc51778f8a65f12a6e59683c74c9`

This is the accepted-main merge commit for PR #93, with parents
`9080913fa8d4806ecf9512c88650c46fa9de77c0` and
`c4c3438db63deee512de6ed753a6861145c4e801`. Git ancestry inspection proves it
is an ancestor of `fe1b748ee48dddd6f01e45214e1f9a23d9724267`, the current accepted
main baseline. Its first-parent delta changes only:

- `deploy/systemd/aios.service`; and
- `tests/unit/core_platform/test_aios_systemd_service.py`.

It is therefore the minimal accepted-main revision containing the already
approved implementation. Later main commits add repository closure and VPS
separation governance records; they are not required in the production
runtime checkout and are deliberately excluded from this deployment target.

## Git-object artifact proof

Inspection of
`2c44dc84cb38dc51778f8a65f12a6e59683c74c9:deploy/systemd/aios.service`
proves:

- Git blob: `8794ee77cea44dae5bb7f96d876d3a240b5a78ed`;
- byte length: `829`;
- SHA-256: `02c4d1ee313b3129b425f3884d794044b3f21916d4ddb9bcfc9c9f8ca2d01281`;
- `Environment=PYTHONPYCACHEPREFIX=/opt/aios/runtime/cache/pycache`; and
- `ReadOnlyPaths=/opt/aios-src`.

Filename identity alone is not sufficient. All three commit, blob, and
SHA-256 identities are mandatory deployment gates.
