# Step 1 Secret Mechanism, Metadata, and Exposure Boundary

## Existing mechanism

`MaterialReceiptRepository.from_environment()` obtains only
`AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD` from the process environment and
constructs the governed candidate runtime configuration. The installed
`aios.service` declares `/opt/aios/runtime/config/runtime.env`; systemd supplies
that file to the service process, and an ephemeral caller executed in the same
governed context must reuse that inheritance mechanism.

No password was printed, copied, tested, logged, embedded in JSON, placed on a
command line, or written to a second file. No human secret entry is required by
the proposed caller model.

## Bounded metadata result

The environment file is a regular non-symlink file with metadata:

| Property | Value |
|---|---|
| Path | `/opt/aios/runtime/config/runtime.env` |
| Owner/group | `root:aiosadmin` |
| Mode | `0640` |
| Runtime readability | Yes, via the `aiosadmin` group |
| Candidate variable-name presence | `AIOS_MATERIAL_RECEIPT_CANDIDATE_DB_PASSWORD` present; value not exposed |

Presence is therefore `PRESENT_CONFIRMED_WITHOUT_VALUE`. Actual credential
validity is `NOT_VERIFIED_IN_STEP_1`; proving validity would require a governed
database capability check in a later stage and is not evidence of absence.

The service's existing environment-file mechanism is authoritative for future
inheritance, subject to a later secret-safe capability gate. Step 1 does not
modify `runtime.env`, restart the service, or contact PostgreSQL.

## Identity and role boundary

The future process identity is `aiosadmin:aiosadmin`. The intended database
runtime role is `aios_material_receipt_candidate_runtime`, with governed
membership in the NOLOGIN writer role
`aios_material_receipt_candidate_writer`. Existing governance supplies this
relationship; Step 1 adds no role or `GRANT` and does not use an owner/admin
role.

## Exposure audit

Static review of the merged Stage 0.33C modules found no candidate password
propagation into the request DTO, authorization artifact, consumed marker,
evidence object, logs, exceptions, Telegram, or Universal Ingestion. The
authorization and consumption records contain bounded identifiers and digests,
never credentials or environment contents.

## Authorization filesystem access model

No production path was provisioned. Logically, the future `aiosadmin` process
can read an artifact provisioned as `root:aiosadmin`, mode `0440`, through its
group membership. It can create an authorization-ID marker in a separately
provisioned `aiosadmin:aiosadmin`, mode `0700` consumed directory, with the
implementation's marker mode `0600`. These are future contracts only and do not
authorize or perform a write.
