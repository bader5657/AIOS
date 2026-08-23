# Owner, Async Dependency, and Lifecycle Decisions

The continuation owner is application orchestration in
`core/ingestion/universal_ingestion.py`, immediately after the exact
`CoreRouteResult` returned by `await aios_core.route(envelope)`. No smaller
existing orchestration helper is present. `AIOSCore` remains a stateless router
and must not import or invoke Brain implementation.

The continuation is native async:

1. await the existing Core route;
2. pass the exact route result and caller-supplied approved semantic inputs to
   the injected/reused `CoreToBrainMapper` exactly once; and
3. await one explicitly injected async Brain boundary dependency with the
   resulting `BrainInput`.

Nested `asyncio.run`, blocking bridges, thread pools, detached tasks, retry, and
fallback are prohibited.

The dependency seam is one typed async callable or a repository-conformant
single-method Protocol equivalent to:

`Callable[[BrainInput], Awaitable[InferenceResult]]`

Naming alone does not justify a new architecture layer. Universal Ingestion
must not directly import `BrainSemanticReceiver`, `BrainInferenceInvoker`, an
InferenceProvider implementation, or Ollama configuration. A prepared
receiver's bound async method may satisfy the seam at a later assembly point.

The application composition layer owns Mapper and receiver lifecycles. Mapper
is constructed once and injected/reused; its UUID factory remains its only
state and it alone creates the Brain request ID. The Receiver is prepared
externally and injected. No concrete provider or environment discovery occurs
inside Universal Ingestion.
