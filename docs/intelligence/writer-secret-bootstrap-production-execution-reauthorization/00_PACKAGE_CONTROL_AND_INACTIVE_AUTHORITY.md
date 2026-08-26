# Writer Secret Bootstrap Production Execution Reauthorization

Date: 2026-08-26 (Asia/Jakarta)

## Frozen source authority

This documentation-only package supersedes the consumed execution authority in
`writer-secret-bootstrap-production-execution-authorization`. It binds a future
one-shot authorization to merged main commit
`aacbf77eb333018a9a2dedf8a4eab66168829e36` and helper path
`scripts/admin/bootstrap_material_writer_secrets.py`.

The mechanically calculated SHA-256 at package creation is:

`34aa8ec5c84606cfa559106bf3d32dc09f45aa98792393e746088e3a64cd5aa0`

The operator must mechanically recalculate this hash immediately before any
authorized invocation. A copied value is not sufficient evidence. Any mismatch
in commit, path, content, transport, or the frozen gates invalidates authority.

## Inactive authority

This package prepares, but does not issue, production execution authority. It
becomes eligible only after its documentation PR is independently reviewed and
merged and the Project Owner explicitly approves one manual execution in a
separate approval act.

If activated, it permits exactly one manually authenticated invocation from the
root of the clean, frozen checkout:

`sudo -- /usr/bin/python3 scripts/admin/bootstrap_material_writer_secrets.py --execute-production`

No wrapper, alternate interpreter, modified helper, extra argument, retry,
automation, or noninteractive sudo is authorized. An invocation consumes the
one-shot authority regardless of success; any subsequent attempt requires fresh
reconciliation, review, artifact freeze, and authorization.

## Present state and exclusions

At preparation time, production writer credentials, writer identities, and the
two governed runtime environment keys are absent. This package creates none of
them and performs no production filesystem, PostgreSQL, Docker, network,
service, Telegram, or business-data mutation.

Runtime credential consumption, service activation/restart, data population,
receipt posting, inventory movement, stock mutation, Telegram, OCR, LLM, and
inference remain outside this package.
