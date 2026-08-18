# Caller and Lifecycle Evidence

Static audit finds exactly one `.register(` call in `core/`, owned by
Universal Ingestion. Asset Pipeline, Document Manifest, and Telegram Adapter
contain no Registry caller.

The call is gated by Pipeline success, true Register handoff readiness, and a
non-empty string Manifest path. Storage, Metadata, Manifest, aggregate-only,
false-readiness, absent-path, and empty-path outcomes produce zero calls. A
ready successful lifecycle produces exactly one call with no retry or fallback.
