# Source Authority and Production Protection

## Required accepted source

The execution source is frozen at accepted repository SHA:

`f164609840f53848977ab0aad9e42ecb2471c9cb`

That SHA contains the accepted Stage 0.7 `OllamaInferenceProvider`, Stage 0.9
`BrainInferenceInvoker`, provider abstraction, inference contracts, and their
accepted verification/closure records.

## Checkout disposition

The production checkout `/opt/aios-src` was observed at
`2c44dc84cb38dc51778f8a65f12a6e59683c74c9`. It is behind the required source
and must remain unchanged. No pull, checkout, reset, merge, service restart, or
other mutation is permitted there.

The preserved Stage 0.8 source
`/opt/aios/runtime/intelligence/staging/stage-0.8-src` was observed at
`d0c8a317e097624f771dc016dcc3f618afc73f70`. It predates Stage 0.9 and is not
eligible for Stage 0.10 execution.

A new detached, clean, temporary checkout is therefore required at:

`/opt/aios/runtime/intelligence/staging/stage-0.10-src`

It must resolve exactly to the required execution SHA. Creating it is an
operator action after this approval activates, not an action in this package.
Immediately before execution, record the checkout SHA and cleanliness and
verify that both `core.brain.inference` and `core.brain.providers.ollama` load
from this same checkout. Do not alter `PYTHONPATH` or imports to mix sources.

## Preservation and cleanup

Record the production and temporary source SHAs before and after the request.
Neither source may change. Do not delete the Stage 0.8 source or the future
Stage 0.10 checkout during approval or execution. Cleanup requires separate
authority.
