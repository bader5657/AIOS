# Future Implementation and Test Requirements

## Candidate paths and implementation gate

Future module candidate:

`core/brain/provider.py`

Future focused test candidate:

`tests/unit/brain/test_provider.py`

These paths are not created or granted implementation authority by this
package. A separate implementation-approval stage must resolve the exact path
set, bounds, interface representation (`ABC` or project-conformant equivalent),
exports, validation behavior, test matrix, regression scope, rollback, and stop
conditions before source or tests change.

## Minimum future focused-test matrix

1. `InferenceProvider` abstract interface exists;
2. `infer` is async;
3. exact `InferenceRequest` input annotation;
4. exact `InferenceResult` output annotation;
5. `ProviderDescriptor` is frozen;
6. `ProviderDescriptor` uses slots;
7. `provider_id` validation;
8. `model_id` validation;
9. exact `ProviderRuntimeKind.LOCAL`/`REMOTE` enum;
10. capabilities are immutable;
11. capability tuple contains exactly `STRUCTURED_INFERENCE`;
12. no credential fields;
13. no endpoint/account fields;
14. no persistence fields or behavior;
15. no retry/fallback API;
16. no tool fields or behavior;
17. no Memory fields/imports;
18. no Specialist fields/imports;
19. no business fields/behavior;
20. direct validated `InferenceResult` construction semantics;
21. exact seven-code failure mapping;
22. Brain-owned timeout and no extension;
23. caller cancellation propagation;
24. raw provider response containment;
25. provider-neutral imports;
26. no Ollama import/type;
27. no remote-provider SDK import/type;
28. no Core reverse dependency;
29. local/remote compatibility without runtime execution;
30. compile/static checks;
31. dependency/import audit;
32. prohibited-source audit; and
33. `git diff --check`.

No provider/runtime/model, live-network, production, VPS, credential, database,
or service test is authorized by this approval.
