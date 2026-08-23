# Project Owner Approval, Activation, and Next Action

## Project Owner approval

I, as Project Owner, approve the narrow Stage 0.14 scope expansion adding only:

`tests/unit/brain/test_inference_contracts.py`

to recognize the already-approved semantic boundary import:

`core/core_to_brain_mapper.py → core.brain.input_contracts`

This exception exists solely so CoreToBrainMapper can construct BrainInput
using the approved semantic contract.

It does not authorize general Core-to-Brain implementation dependencies,
receiver/invoker/provider imports, Core wiring, production integration,
inference, or any fourth path.

## Publication and activation

The allowed diff for this approval is this governance package only.
Publication requires a normal clean, mergeable PR into `main`, without force or
history rewrite. After merge and synchronized clean-main audit, authority
activates as:

`INTELLIGENCE STAGE 0.14 NARROW MAPPER DEPENDENCY SCOPE EXPANSION APPROVED — READY TO RESUME IMPLEMENTATION`

Activation modifies no implementation or runtime.

## Next official action

Resume `implementation/intelligence-stage-0.14-core-to-brain-mapper`, update
only the exact dependency-policy test, rerun the complete approved non-live
verification matrix, and publish the three-path mapper implementation only if
all gates pass.
