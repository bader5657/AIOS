# Test and Regression Gates

## Focused path and minimum matrix

The sole focused test path is `tests/unit/brain/test_provider.py`. It must cover
at least these 40 gates; parameterization may produce a larger pytest count:

1. exact `ProviderRuntimeKind` values;
2. no enum aliases;
3. frozen `ProviderDescriptor`;
4. slotted `ProviderDescriptor`;
5. valid `provider_id`;
6. invalid/non-string/blank/control-character `provider_id`;
7. 128-character provider bound and 129-character rejection;
8. valid `model_id`;
9. invalid/non-string/blank/control-character `model_id`;
10. 128-character model bound and 129-character rejection;
11. actual runtime-kind enum required;
12. defensive immutable capability tuple;
13. exactly `STRUCTURED_INFERENCE` accepted;
14. empty capabilities rejected;
15. duplicate capabilities rejected;
16. unsupported/string/wrong-type capability rejected;
17. no credential fields;
18. no endpoint/account fields;
19. no persistence fields;
20. no retry fields/API;
21. `InferenceProvider` is abstract;
22. `infer` is abstract;
23. `infer` is async;
24. exact `InferenceRequest` parameter annotation;
25. exact `InferenceResult` return annotation;
26. no model/provider/config/timeout/tool override argument;
27. no credential argument;
28. valid LOCAL descriptor without execution;
29. valid REMOTE descriptor without execution;
30. no network implementation/import;
31. no subprocess/model execution;
32. no Ollama import/type;
33. no remote-provider SDK import/type;
34. no Core reverse dependency;
35. no Memory import/field;
36. no Specialist import/field;
37. no business import/field;
38. compile/static import gate;
39. dependency/import audit; and
40. `git diff --check`.

Tests must additionally confirm the abstract descriptor property and closed
four-field descriptor schema. Static negative assertions do not authorize any
prohibited provider name or behavior in production source.

## Regression matrix

Future implementation verification must run and record:

- focused provider tests;
- Stage 0.3 inference-contract tests;
- existing Core regressions;
- relevant Domain regressions;
- Stage 8/9 critical dependency/import/service/privacy gates;
- complete repository suite where no live production/VPS service is needed;
- compile/static checks;
- prohibited-source audit;
- dependency/import-direction audit; and
- `git diff --check` plus exact two-path closed-world diff.

No production, VPS, live-provider, model, network, credential, or database test
is required or authorized.
