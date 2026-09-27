# Telegram authentication evidence retention

This implementation captures future challenge messages. It does not authenticate
the existing PR #305 attempt, merge governance, commission a process, or grant
production/recovery authority. A capture is not an authentication PASS.

## Receiver behavior and closed schema

Immediately before text normalization, the existing receiver projects only these
fields from a direct Telegram `Update.message` into canonical evidence:

```json
{
  "schema_version": "aios-telegram-owner-auth-evidence-v1",
  "update_id": 901,
  "message": {
    "message_id": 51,
    "from": {"id": 961959058, "username": "bagusder21"},
    "date": "2026-09-28T01:00:10.000000Z",
    "chat": {"id": 961959058, "type": "private"},
    "text": "AIOS-PO-AUTH-PR305-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "local_received_at_utc": "2026-09-28T01:00:10.123456Z"
}
```

The example is synthetic, not authentication evidence. Username is nullable when
absent. IDs are strict integers (booleans rejected). Timestamps are UTC RFC3339
with six fractional digits; Telegram's second-resolution date is represented with
zero microseconds. Unknown/missing fields and duplicate JSON keys at every level
are rejected. Only exact `AIOS-PO-AUTH-PR[1-9][0-9]*-[A-Za-z0-9_-]{43}` messages
are captured; whitespace and case are not normalized. The nonce format supports
32 random bytes encoded as unpadded URL-safe base64. Issuers must generate fresh,
cryptographically random nonces; this receiver does not issue challenges.

Canonical encoding uses `ensure_ascii=False`, `sort_keys=True`,
`separators=(",", ":")`, `allow_nan=False`, UTF-8 and exactly one trailing LF.
Validation compares the original bytes with their canonical re-encoding.
No tokens, headers, names, captions, arbitrary update extras, or unrelated messages
are retained in this evidence path. The event-loop handler prepares immutable
canonical bytes from the original Update **before normalization**, then offers
those bytes to a single dedicated filesystem worker. Persistence can finish after
normalized ingestion; fields are never reconstructed from a normalized manifest.

Admission is bounded to **one running job and zero waiting jobs**. A nonblocking
slot rejects excess authentication captures immediately (`REJECTED_CAPACITY`,
logged as `NOT_PUBLISHED: capacity exhausted`). No per-message asyncio task or
unbounded executor backlog is created. The slot remains occupied until the worker
finishes, including during stalled I/O; no timeout releases it prematurely.
Ordinary messages bypass the worker. Existing ingestion receives the original
message exactly once, whether admission succeeds, is rejected, or capture fails.
Capture never calls authentication or consumption. Generic failure/state messages
contain no Update contents, credentials, paths or exception details. There is no
automatic retry of rejected or failed captures.

## Storage and directory identity

Default archive: `/opt/aios/data/authentication-evidence/telegram/`.
Evidence filenames remain `<UUID>.<transport-SHA256>.json`; the hash includes LF.
Each successful evidence publication has a `<filename>.complete` certificate.
The evidence's closed schema is unchanged; certificates and directory identity
metadata are separate private control records, not additional platform fields.

All path components are opened from `/` using directory descriptors with
`O_DIRECTORY | O_NOFOLLOW`. The walk rejects traversal, symlinks, non-directories,
and unsafe owners/permissions. Ancestors must be root/custodian-owned and not
otherwise writable; a root-owned sticky temporary ancestor is allowed for private
test archives. The archive, its parent and `consumed/` must be custodian-owned and
private (0700). Newly created components use 0700. Files use 0600.

Each descriptor pins device, inode, uid, gid and mode. These identities are checked
against `fstat` and no-follow, parent-descriptor-relative entry metadata throughout
the operation. Temporary creation, file reads, publication links, cleanup, syncing
and consumption are descriptor-relative. A replaced pathname cannot redirect I/O
into the replacement directory. An observed identity change fails closed.

The exclusive parent anchor
`/opt/aios/data/authentication-evidence/.telegram.auth-identity.json` retains the
entire directory chain and consumption-directory identity. The process also
remembers an initialized path's identities, refusing to establish a new namespace
if an ancestor or anchor disappears. The retained anchor detects archive and
consumption-directory replacement across process reopen/restart. Preserve the
anchor, its trusted parent, evidence, and consumption directory as one custody
boundary. Deleting/replacing that whole boundary is not supported recovery or
re-enrollment; hashes cannot defend against a custodian intentionally replacing
all trust metadata. Missing anchors in verification are always STOP.

## Publication outcomes and durability

Publication reports three states:

| State | Retained outcome and authentication consequence |
|---|---|
| `NOT_PUBLISHED` | This attempt did not publish its final payload filename. Layout or temporary artifacts may exist. Existing records are never overwritten. No new authentication evidence is accepted. |
| `PUBLISHED_DURABILITY_UNCERTAIN` | The final payload may be complete, but a required directory sync, identity check, readback or completion publication failed. Preserve the payload for inspection; its absence must not be inferred. No completion certificate is issued, so verification rejects it and cannot consume a challenge. |
| `DURABLY_PUBLISHED` | Payload file and parent directory syncing, exact readback and identity checks succeeded; the final completion certificate was published. Capture alone is still not authentication PASS. |

The worker writes/fsyncs the private payload and completion staging files, then
atomically hard-links the payload without replacement. It fsyncs that directory,
checks the published bytes and directory identities, and **only then** links the
completion certificate without replacement. The completion link is the final
commit point: no required fallible fsync/check follows it. Best-effort staging
cleanup cannot change the reported outcome and never deletes final evidence.
Directory creation includes parent-directory fsync.

The completion link itself deliberately has no following fsync whose failure could
leave a falsely successful certificate. A crash may therefore lose that link even
though the payload is durable. That causes denial of authentication, never
promotion of uncertain data. Verification requires the exact certificate bytes
and payload digest. It does not manufacture a certificate, retry publication,
delete uncertain evidence or infer success from a JSON file's existence. This is
durable local evidence retention, not a signature or independently immutable store.

## Verification and replay

The receiver never calls `verify_and_consume`. An explicitly authorized operator
can call that function with the trusted archive path and a `ChallengeBinding`
constructed from the previously issued challenge, not from received content.
The binding supplies exact challenge text, PR number, HEAD, approval UUID, expected
numeric sender ID, declared username and issue/expiry timestamps. The operator
must verify these inputs against the retained issuance record and current subject
before invoking it. This helper does not query GitHub or certify merge readiness.

Verification checks the closed canonical schema and filename digest, exact text,
numeric sender identity, exact username if present, and a private chat whose ID
equals the sender. Both Telegram time and local receipt must be in the challenge
window; the issue boundary permits Telegram's second precision, while local
receipt must be at or after the precise issue time. Verification can occur later
than expiry if the evidence was received within the window. A missing username
does not invent a verified display name; the receipt separates actual username
from the declared display username.

Only after all checks succeed does descriptor-relative, no-replace publication
create `consumed/<SHA256-of-challenge-text>.json` and its completion certificate.
The receipt binds the source digest, numeric identity, PR/HEAD, approval ID,
validity window and disclosed `solo-project-owner-bootstrap` roles. Concurrent
or later attempts with the same challenge cannot create another successful
consumption. The anchored consumption directory cannot be replaced to reset this
check. Capture overload and invalid/uncertain evidence never enter consumption.

If consumption publication itself fails after its payload link, report uncertainty,
not authentication PASS. The retained filename conservatively reserves the
challenge against retry, even if its completion certificate is missing. Preserve
it for inspection; never delete it to reuse a nonce. Use a separately issued new
challenge. No failed identity/text/time/schema check writes a consumption record.

Filesystem custody is part of the trust boundary. Hashes do not authenticate a
hand-written file; accept only the existing receiver's controlled archive, never
an uploaded or copied JSON record. Old incomplete manifests fail the schema;
the previous challenge and its sources remain unchanged and unconsumed. Use a
new challenge after a separately approved deployment.

## Deployment and rollback

This PR does not deploy or restart production. Using capture requires deploying
the two receiver Python files and a separately authorized service restart. Confirm
the service account can create the dedicated archive under `/opt/aios/data`.
No database migration, configuration secret, new polling consumer, webhook, or
logging reconfiguration is required.

Rollback restores the **pre-feature** receiver under separate deployment approval
and restarts the host `aios.service` only if authorized. Keep the archive, identity
anchor, completion certificates and consumption records unchanged; a code-only
rollback leaves them intact. Do not use the superseded draft verifier from PR #306
HEAD `796c551`: it does not enforce completion certificates and must not verify
uncertain evidence. While capture/verification is rolled back, no challenge may be
authenticated from a normalized manifest alone.

This change requires no database migration or new config/environment variable.
It creates private evidence/control files only when a future deployed receiver
admits a challenge. It does not migrate or promote old evidence. Moving/restoring
archive directories with new inode/device identities is not a transparent rollback:
the identity checks deliberately STOP and require a separately reviewed custody
recovery decision. No such recovery is implemented or authorized here.
