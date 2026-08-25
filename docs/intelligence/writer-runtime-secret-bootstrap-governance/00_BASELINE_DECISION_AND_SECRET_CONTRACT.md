# Writer Runtime Secret Bootstrap Governance

Date: 2026-08-25 (Asia/Jakarta)

## Baseline

Writer provisioning stopped at the secure-secret preflight with no production
role change. No database transaction began, no password was generated, and the
provisioning-session count remains zero. PostgreSQL remained healthy; all three
receipt/movement tables remained empty; `material_stock` and
`aios_material_stock_reader` remained unchanged; and all four planned writer
identities remained absent.

The governed secret file is `/opt/aios/runtime/config/runtime.env`, owned by
`root:aiosadmin` with mode `0640`. Its parent config directory is on the same
filesystem. Non-interactive `sudo` is unavailable, and the automation identity
must not work around that boundary.

## Approved variables

Repository/runtime convention uses uppercase underscore-separated environment
keys. The inspected file has 11 assignments, five comments, five blank lines,
no invalid lines, no duplicate keys, and a final newline. Values were not
printed. Freeze exactly:

- `AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD`
- `AIOS_MATERIAL_INVENTORY_POSTING_DB_PASSWORD`

Each value is independently generated from at least 32 CSPRNG bytes and encoded
as unpadded Base64URL (`A-Z`, `a-z`, `0-9`, `_`, `-`; 43 characters for 32
bytes). The values must differ. Human selection, reuse, fallback defaults, and
password hashes in governance evidence are prohibited.

## Security decision

Approve a one-time root-mediated bootstrap. Reject group/world-writable
`runtime.env`, broad or persistent sudo capability, Git storage, manual
copy/paste, and caller-supplied secret values. The final file remains
`root:aiosadmin` mode `0640`.
