# Project Owner Approval, Publication, and Activation

## Project Owner approval

I, as Project Owner, authorize a disposable, non-production disk-layout measurement of the exact pinned Ollama 0.32.13 linux/amd64 image solely to determine its compressed, unpacked, persistent, and acquisition-peak footprint.

No Ollama runtime execution, model download, inference, production activation, AIOS service change, database change, or resource-ceiling change is authorized.

The existing 6 GiB staging ceiling remains unchanged.

## Reviewer gates

- synchronized clean approval baseline;
- exact image, platform, and digest pin;
- isolated disposable environment and production-store prohibition;
- enforceable 6 GiB hard quota and independent host reserve;
- model acquisition and runtime execution prohibited;
- exact measurement evidence and combined-footprint formulas;
- fail-closed PASS, CONDITIONAL_PASS, and FAIL definitions;
- bounded cleanup and protected-service requirements;
- no source, service, configuration, dependency, VERSION, production, or VPS
  mutation;
- provenance reconciliation retained as a separate blocker.

## Publication and activation

- branch: `governance/intelligence-stage-0.6.2-disposable-image-measurement`;
- allowed diff: this governance package only;
- publication: normal CLEAN/MERGEABLE pull request into `main`;
- force push/history rewrite: prohibited;
- installation, model download, container execution, inference, service action,
  and production mutation: none.

Merging the governance PR activates measurement authority only. It does not
perform or authorize production installation, model acquisition, Ollama
execution, inference, provider-adapter work, Brain activation, or production
use.

## Next official action

Perform the exact controlled disposable Ollama image-layout measurement under
this package. Verify identity before acquisition, preserve the hard quota and
host reserve, collect before/peak/after evidence, remove only disposable
artifacts, and report PASS, CONDITIONAL_PASS, FAIL, identity mismatch, or
insufficient measurement evidence.

Do not acquire the Qwen model. After disk classification, Stage 0.6.2 still
requires an exact canonical-model to Ollama-artifact provenance record before
runtime/model governance approval.
