# Suppression, Preservation, and Storage Limit

| Failure owner | Verified suppression | Verified preservation |
|---|---|---|
| Storage | Metadata 0; Manifest 0; Registry 0; Event 0; Core 0 | No completed stored-path claim |
| Metadata | Manifest 0; Registry 0; Event 0; Core 0 | Stored original |
| Manifest | Registry 0; Event 0; Core 0 | Original and completed metadata; no completed Manifest |
| Registry | Event 0; Core 0 | Original, metadata, completed Manifest; no failed committed row |
| Event | Core 0 | Original, metadata, Manifest, committed Registry row |
| Core | Brain 0 | Original, metadata, Manifest, Registry row, completed Event result |

No downstream failure rolled back an already completed upstream artifact.
Earlier successful Event handler effects remain intentionally non-transactional.

Telegram temporary-download cleanup was verified. Complete cleanup of every
partially created destination after an arbitrary mid-copy filesystem failure is
not guaranteed by the current Storage contract and is not a Stage 8 exit-gate
requirement without separate authority.
