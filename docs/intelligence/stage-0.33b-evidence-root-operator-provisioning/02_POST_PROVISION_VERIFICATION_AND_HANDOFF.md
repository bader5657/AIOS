# Stage 0.33B-FP Post-Provision Verification and Handoff

## Operator-to-Codex boundary

After this package is independently reviewed and merged, Codex stops and presents
the exact two governed commands to the human operator. Codex does not execute
them. After the operator reports completion, Codex may perform only the bounded
non-mutating path verification and non-privileged write-capability probe governed
below. No production PostgreSQL connection is permitted.

## Non-mutating path verification

Using bounded `lstat`/`stat` inspection without following symlinks, require:

| Path | Type | Symlink | Owner:group | Mode |
|---|---|---|---|---|
| `/opt/aios/runtime/intelligence/production-execution-evidence` | directory | NO | `root:root` | `0755` |
| `/opt/aios/runtime/intelligence/production-execution-evidence/stage-0.33b-d` | directory | NO | `aiosadmin:aiosadmin` | `0750` |

Any mismatch classifies FILESYSTEM PROVISIONING VERIFICATION BLOCKED. Do not
repair, contact PostgreSQL, or consume Migration authority.

## Bounded aiosadmin write-capability proof

Only after exact path verification, authorize one non-privileged probe executed
as `aiosadmin` inside the Stage root. Its filename is
`.provisionability-probe-<canonical-lowercase-UUIDv4>`. Generate one UUID, create
the file exclusively without following symlinks, and fail closed on collision;
do not choose another name or overwrite anything.

The probe must have mode `0600`, owner/group `aiosadmin:aiosadmin`, and exact
contents:

```text
AIOS_STAGE_0_33B_D_EVIDENCE_ROOT_PROBE
```

Write no timestamp, credential, environment value, business data, or arbitrary
content. Flush and fsync the probe, verify its exact owner/group/mode and bounded
contents, then delete only that exact probe. No sudo and no other cleanup or file
deletion is authorized.

PASS requires exclusive creation, write, flush, fsync, owner `aiosadmin`, group
`aiosadmin`, mode `0600`, and exact-probe cleanup all PASS. Any failure classifies
FILESYSTEM PROVISIONING VERIFICATION BLOCKED; do not contact production
PostgreSQL. Migration authority remains UNCONSUMED.

## Bounded provisioning record

Provisioning records may contain only bounded, secret-free facts: governed paths;
owner/group/mode and symlink results; `/usr/bin/sudo` and `/usr/bin/install`
identities; whether Command A or Command B was required; bounded command success
or failure status; write-probe PASS/BLOCKED; and final provisioning
classification.

Provisioning records must not contain a sudo password, password-prompt response,
terminal password input, credential-bearing shell history, environment contents,
environment-variable dumps, `runtime.env` contents, `DATABASE_URL`, database
password, credential-bearing DSN, token, bot token, API key, private key, PRIVATE
KEY material, SSH private key, arbitrary environment/configuration dump, raw
business data, sudo conversation, or broad sudo policy dump. Command stdout,
stderr, environment, and shell state are not captured without bounded
sanitization.

On failure, retain only bounded sanitized information such as operation
identifier, safe failure class, safe exit/result state, and path identifier. Do
not retain a complete environment, sudo conversation, authentication input,
credential-bearing stderr, or secret-bearing shell state. If an error message
unexpectedly contains secret material, do not copy that material into any
governance, provisioning, audit, verification, or operator record.

## Handoff and activation order

The frozen order is:

1. this governance package receives independent PASS and merges unchanged;
2. inspect the existing parent and both governed destination paths;
3. the human operator runs Command A only if its path is absent;
4. the human operator runs Command B only if its path is absent;
5. Codex performs bounded non-mutating post-provision path verification;
6. Codex performs the bounded non-privileged probe and exact cleanup;
7. record Stage 0.33B-FP PASS or BLOCKED and return to governance;
8. only after PASS, return to PR #249 and bind its activation contract to the
   already provisioned and verified persistent root;
9. conduct a new independent review of PR #249 before any merge or activation.

This package does not authorize a Stage 0.33B-D evidence session, production
Docker/`psql` launch, Migration 0005 or 0004, Stage 0.33B-V, runtime activation,
or candidate traffic. PR #249 remains open, unmerged, and blocked solely on
evidence-root provisionability throughout this publication task.

```text
STAGE 0.33B-FP OPERATOR EVIDENCE-ROOT PROVISIONING GOVERNANCE PUBLISHED
— EXACT PRIVILEGED COMMANDS FROZEN
— SUDO PASSWORD REMAINS HUMAN-ONLY
— READY FOR INDEPENDENT GOVERNANCE REVIEW
— NO FILESYSTEM PROVISIONING PERFORMED
— MIGRATION 0005 AUTHORITY REMAINS UNCONSUMED
— PRODUCTION CANDIDATE ACTIVATION NOT AUTHORIZED
```
