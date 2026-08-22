# Sequence, Fallback, and Production Boundary

## Mandatory sequence

The required order is:

1. selection governance;
2. exact model candidate and pinned runtime governance;
3. runtime installation approval;
4. isolated staging installation;
5. controlled benchmark;
6. provider adapter implementation;
7. contract verification;
8. operational review; and
9. separate production decision.

No step may infer authority from a later step or skip staging.

## Provider adapter status

`OllamaInferenceProvider` is only a future candidate after separate runtime and
model selection/implementation approval. It is not implemented or authorized
here. Any future adapter must conform to existing `InferenceProvider` without
changing that abstraction for Ollama convenience.

## Retry and fallback

- retry: `NONE`;
- fallback: `NONE`;
- alternate model: `NONE`;
- alternate provider: `NONE`.

## Remote fallback strategy

A generic REMOTE provider is the `SECOND-BEST FUTURE STRATEGY`, not an active
fallback. It may return for governance evaluation only if local structured
quality is inadequate, resource ceilings cannot be met, latency is
unacceptable, or staging benchmark fails.

Remote use still requires explicit outbound-network authority, provider
approval, privacy/retention review, credential governance, and cost ceiling.

## Protected production boundary

Stage 0.6.1 changes no `aios.service`, AIOS Core, Registry, Event Engine,
Telegram, Storage, PostgreSQL, production compose topology, dependency,
VERSION, production state, or VPS state.
