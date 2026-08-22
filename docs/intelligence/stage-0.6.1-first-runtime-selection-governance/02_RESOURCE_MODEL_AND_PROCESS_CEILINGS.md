# Resource, Model, and Process Ceilings

## Hard staging ceilings

| Resource | Approved maximum |
|---|---|
| Runtime/container RAM | `3 GiB` hard limit |
| CPU | `1 vCPU` equivalent; conceptually `CPUQuota=100%` or equivalent container limit |
| Model file | `2 GiB` |
| Total runtime/model disk | `6 GiB` including runtime/container layers and bounded temporary files |
| Loaded models | `1` |
| Concurrent inference | `1` |
| Pending queue | `1`; excess fails closed |
| Runtime timeout ceiling | `120,000 ms` |

Brain request timeout may be shorter. The runtime may never extend beyond the
request timeout. These are ceilings, not installation or consumption authority.

## Approved model class and purpose

Only a `VERY-SMALL / AGGRESSIVELY QUANTIZED MODEL CLASS` is eligible for the
first staging benchmark, conceptually sub-2B where practical.

No 7B, 8B, larger, multi-model, or production-local model is approved. The
exact model name is intentionally deferred to separate model-selection
governance.

The model milestone proves only:

`InferenceRequest → provider/model → validated structured InferenceResult`

It does not prove or authorize general Brain reasoning, autonomous
intelligence, Memory, Specialists, tools, business decisions, or agent
orchestration.

## Process isolation

Future staging must use a separate isolated container with:

- independent lifecycle and resource limits;
- no shared restart ownership with `aios.service`;
- no production compose modification under this approval; and
- failure containment from AIOS, PostgreSQL, and Telegram polling.

The runtime must not be a dependency of AIOS/PostgreSQL startup or health.
