# Evidence Class, Risk, and Governance Sufficiency

## Classification

Evidence class: `C — STRONGLY_RECONCILED`.

Level A is unavailable because no authoritative revision → conversion → blob
hash chain is published. Level B is unavailable because Ollama does not name an
exact canonical revision. Level D does not apply: there is one official Ollama
artifact frozen by digest, and its detailed architecture, tokenizer, model
identity, quantization, size, template, and license reconcile with the named
canonical Qwen model. No competing upstream model identity was found.

Correct limitation wording:

`canonical model family/repository verified; exact source revision of the Ollama conversion not independently attested`

## Governance requirement

Stage 0.6.2 required canonical Qwen-to-Ollama artifact provenance
reconciliation before installation authority. It did not expressly require a
signed or cryptographically reproducible conversion chain. The prior Stage
0.6.3 evaluation treated such a chain as the only closure path; that was a
conservative remediation standard, not an explicit Stage 0.6.2 requirement.

For controlled staging, class C is sufficient with the stated limitation
because:

- the official Ollama namespace and detailed blob metadata identify the model;
- manifest and blob digests prevent silent artifact substitution;
- canonical owner, model family, architecture, tokenizer, and license match;
- exactly one model is allowed, without retry, fallback, or dynamic routing;
- staging remains isolated, resource-bounded, and benchmark-gated; and
- installation, Brain integration, production use, and business use are not
  granted by this reconciliation.

This sufficiency applies only to rerunning the isolated staging installation
approval. It does not establish production-grade supply-chain provenance.

## Security risk

There is no affirmative evidence of compromise, model substitution, license
mismatch, or identity ambiguity. Residual risk is the inability to independently
reproduce the Ollama blob from a named canonical revision and converter. Pinned
digests contain this risk to the reviewed immutable artifact but do not remove
the lineage uncertainty.

Controlled-staging risk is `LOW TO MODERATE / ACCEPTABLE WITH LIMITATION` under
the existing isolation, resource, no-secret, no-production, and mandatory
benchmark controls. Production risk is not accepted or evaluated here.
