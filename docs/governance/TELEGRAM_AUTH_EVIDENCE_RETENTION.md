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
are retained in this evidence path. The existing normalized ingestion continues
with the original message object, including after a capture failure; only a generic
failure is logged, without message or exception contents. A failure leaves no
usable new evidence and never authenticates or consumes a challenge.

## Storage and verification

Default archive: `/opt/aios/data/authentication-evidence/telegram/`.
Evidence filenames are `<UUID>.<transport-SHA256>.json`; the hash includes the LF.
Private files (0600) are fsynced before atomic no-replace publication, followed by
directory fsync. Newly created leaf directories are 0700. Existing archive
directories must belong to the custodian and not be group/world writable.
This is durable local retention, not a signature or independently immutable store.

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

Only after all checks succeed does an atomic no-replace consumption receipt appear
at `consumed/<SHA256-of-challenge-text>.json`. This binds the source evidence digest,
numeric identity, PR/HEAD, approval ID, validity window and disclosed
`solo-project-owner-bootstrap` roles. Concurrent or later attempts with the same
challenge fail. Preserve this directory permanently alongside evidence. A crash
after publication may leave a consumed marker even if the caller did not receive
success; inspect it, never delete it to retry. No failure is reported as PASS.

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

Rollback restores the previous receiver code under a separate deployment approval
and restarts the service if authorized. Preserve the evidence and consumption
archive unchanged; rollback must never reset replay protection. Capture becomes
unavailable until restored, so no new challenge may be marked authenticated from
the normalized manifest alone.
