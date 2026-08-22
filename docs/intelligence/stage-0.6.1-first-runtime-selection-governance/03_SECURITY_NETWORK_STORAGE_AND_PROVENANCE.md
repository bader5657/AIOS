# Security, Network, Storage, and Provenance

## Bind and network boundary

Future staging exposure must be loopback/private-only or confined to an
isolated internal container network. No public inference endpoint is approved.
Exact topology is deferred to runtime implementation approval.

After verified model acquisition, the LOCAL runtime must require no outbound
network. Acquisition itself requires separate controlled download and
provenance authority; this package grants none.

## Model storage

Model files are runtime assets, not source, persistence, or Memory. They must
remain outside Git and `/opt/aios-src`. The conceptual root is:

`/opt/aios/runtime/models/`

The exact path, ownership, permissions, and lifecycle require runtime
implementation approval. No directory or file is created here.

## Provenance and version pinning

Before any download/installation, separate approval must record:

- exact model identity and upstream/source;
- exact version/revision;
- quantization;
- model file size;
- checksum/hash where available;
- license and use review; and
- a durable provenance record.

Floating `latest` model authority is prohibited.

Ollama must also be pinned by exact version or exact container digest/version
before installation. An unpinned `latest` runtime is prohibited.

## Security and data boundary

Future staging must execute non-root where possible, expose no public endpoint,
contain no production secret unless separately necessary and approved, log no
prompt/response by default, retain no request/result history, execute no
tool/shell/business action, and remain outside Core ownership.

There is no inference persistence: no conversation/prompt/response history,
embeddings, session, cache treated as Memory, or provider-result store.
