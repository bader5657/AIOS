# Disposition Options Assessment

## Option A — ADAPT

Literal reuse is approximately **20–30%**: class/component shell, sequential
control-flow shape, local source guard candidate, and result-container concept.
Approximately **70–80%** is obsolete, prohibited, or missing: the entire public
signature, enum/status semantics, result fields, all three dependency call
contracts, image-only storage assumption, Request Context integration, ten-input
coverage, failure result, multi-file behavior, and production integration.

Adapting the file would require preserving its identity while rewriting most
meaningful lines. Complexity is medium and review risk is medium-high because
old names and structure would suggest authority the code no longer has.

**Assessment: NOT SELECTED.** It fails the requirement that most implementation
be retainable and is not the simplest option.

## Option B — REPLACE

Retain only these concepts as design evidence:

- a small bounded Asset Pipeline component;
- explicit sequential orchestration;
- delegation rather than reimplementation of Stage 3 semantics;
- a bounded result returned after successful handoffs; and
- the JPEG happy path as one future test scenario.

Discard the historical runtime and write a minimum contract-first component
against current capabilities after implementation approval. Expected size is
small: one pipeline module plus package marker, with no separate state module,
and focused tests. Integration changes, if authorized, remain narrow.

Complexity is low-to-medium and risk is lowest because obsolete APIs and state
semantics cannot leak accidentally.

**Assessment: SELECTED.**

## Option C — REJECT

Current Universal Ingestion already performs much of the Stage 3 sequence, but
that does not eliminate the Blueprint-named Asset Pipeline requirement. The
frozen Execution Plan explicitly requires a Stage 4 runtime and verified
`Request Context → Asset Pipeline → Document Manifest` path.

Rejecting Asset Pipeline runtime would contradict the active execution path
and Stage 4 exit gate.

**Assessment: NOT SELECTED.**
