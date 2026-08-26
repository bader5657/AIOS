# Writer Secret Bootstrap Production Execution Authorization

Date: 2026-08-26 (Asia/Jakarta)

## Frozen source authority

This documentation-only package freezes the helper artifact introduced by merge
commit `4fc068532f197d399600229d73d5e570bee6bd74` at helper path
`scripts/admin/bootstrap_material_writer_secrets.py`.

The mechanically calculated SHA-256 of that helper is:

`83e2723acf9efd5f56325cc3beb96c4354a5b124e5196d914681b0b13d4d5384`

Execution authority is invalid if the commit, path, content hash, or any frozen
target below differs. The operator must calculate and compare the helper hash
immediately before execution; a copied value alone is not evidence.

## Authority granted

Subject to every preflight and stop gate in this package, the Project Owner may
separately authorize exactly one manually authenticated `sudo` invocation:

`sudo -- /usr/bin/python3 scripts/admin/bootstrap_material_writer_secrets.py --execute-production`

The command must be issued from the root of the clean source checkout after this
governance package is merged, with `HEAD`, `main`, and `origin/main` identical.
The execution evidence records that governance merge commit and proves the helper
path still has the frozen SHA-256. The exact
repository helper path is `scripts/admin/bootstrap_material_writer_secrets.py`.
No unverified absolute deployment path, alias, wrapper, environment activation,
repeated attempt, modified helper, or alternate argument is authorized.

This package does not itself activate that command. An authenticated human must
approve the one execution immediately before it occurs.

## Present state and exclusions

Creation and publication of this package generate no credentials and perform no
production filesystem or PostgreSQL mutation. They do not create writer roles,
populate data, modify runtime services, or change Telegram behavior.

Application credential consumption, service activation/restart, business-data
population, receipt posting, stock mutation, Telegram, OCR, LLM, and inference
remain outside this authority.
