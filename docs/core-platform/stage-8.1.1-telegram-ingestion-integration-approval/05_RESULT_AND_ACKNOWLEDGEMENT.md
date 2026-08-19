# Result, Failure, and Acknowledgement Contract

The smallest existing success convention is
`IngestionResult.register_handoff_ready`. A general receipt acknowledgement may
be delivered only after the single delegated call returns with that flag true.
This is an adapter-level bounded ingestion acceptance; it is not a claim that
Registry, Event Engine, AIOS Core, or a completed business response succeeded.

| Condition | Required adapter disposition |
|---|---|
| malformed update/no usable message/required transport identity absent | return at transport boundary; no ingestion, RequestContext, or fabricated data |
| unsupported input (`UNKNOWN`) | bounded non-success; no generic success acknowledgement |
| empty content | bounded non-success; no generic success acknowledgement |
| Storage/download failure reflected as no ready handoff | preserve bounded failure; no success acknowledgement |
| delegated exception/bounded ingestion failure | propagate/preserve the existing bounded path; no success acknowledgement |
| ready handoff | existing receipt-style acknowledgement may be delivered |

No new global failure taxonomy or application retry is authorized. Registry
failure codes, Event Engine results, and CoreRouteResult must not be interpreted
by the adapter. `APPLICATION RETRY = NONE`; no loop, backoff, download retry, or
ingestion retry may be introduced.
