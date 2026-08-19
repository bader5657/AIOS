# Runtime Correction and Stop Conditions

No runtime correction is authorized by this package.

If the focused test proves a concrete violation of active authority, implementation
must stop with:

`STAGE 8.1.3 RUNTIME CORRECTION APPROVAL REQUIRED`

The report must identify the exact failing rule, exact implicated runtime path,
smallest proposed correction, and evidence that the test matches active authority.
Runtime must not be patched until separate Project Owner approval is published.

Any need for a second implementation path must instead stop with
`STAGE 8.1.3 SCOPE EXPANSION REQUIRED`.
