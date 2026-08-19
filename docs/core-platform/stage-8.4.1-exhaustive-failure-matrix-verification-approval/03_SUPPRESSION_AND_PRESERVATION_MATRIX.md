# Suppression and Preservation Matrix

| Failure owner | Mandatory later-stage suppression | Mandatory preservation |
|---|---|---|
| Storage | Metadata 0; Manifest 0; Registry 0; Event 0; Core 0 | No completed stored path is claimed; current temporary-download cleanup only |
| Metadata | Manifest 0; Registry 0; Event 0; Core 0 | Stored original |
| Manifest | Registry 0; Event 0; Core 0 | Original and completed metadata; no valid completed Manifest |
| Registry | Event 0; Core 0 | Original, metadata, completed Manifest; no committed failed Registry row |
| Event | Core 0 | Original, metadata, Manifest, committed Registry row |
| Core | Brain 0 | Original, metadata, Manifest, committed Registry row, completed Event result |

For `HANDLER_FAILURE`, effects of earlier successful handlers are intentionally
non-transactional and remain. The matrix must not assert their rollback.

No downstream failure rolls back, deletes, rewrites, relocates, or reruns an
already completed upstream artifact.
