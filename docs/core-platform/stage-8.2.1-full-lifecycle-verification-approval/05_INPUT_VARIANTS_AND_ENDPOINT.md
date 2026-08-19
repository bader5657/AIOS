# Input Variants and Endpoint

The primary path uses one stable file-backed Telegram input and verifies that
the original remains preserved. Secondary evidence must cover or directly reuse
accepted evidence for:

- text: RequestContext → Metadata → Manifest → Register → Process → Route → Respond, with Store Original not applicable; and
- Web/YouTube URL: exact source text into Metadata, Manifest, and Registry,
  followed by Process, Route, and Respond, with no remote retrieval.

The happy path uses one DomainEvent specifically to exercise Process and Route.
The production rule remains zero or one caller-supplied DomainEvent.

The endpoint is the existing Telegram acknowledgement after bounded
`AIOS_BRAIN_BOUNDARY` readiness. Brain invocation is zero.
