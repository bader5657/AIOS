# Test, Regression, and Dependency Gates

## Focused test path and matrix

The sole focused test file is
`tests/unit/brain/test_inference_contracts.py`. It must cover at least these 35
numbered gates (individual parameterized cases may make the pytest test count
larger):

1. frozen classes;
2. slots and no instance `__dict__`;
3. exact schema version;
4. unsupported version rejection;
5. exact sole capability enum;
6. required request fields;
7. optional request fields;
8. prohibited-field absence;
9. correlation/request ID bounds;
10. timeout bounds;
11. output-schema-reference bounds;
12. input payload JSON compatibility, finite numbers, depth/member/byte bounds;
13. recursive defensive immutability;
14. context-reference count and item bounds;
15. request and result serialization round trips and JSON dumpability;
16. missing and unknown wire-field rejection;
17. exact seven `FailureCode` members and values;
18. result success invariant;
19. result failure invariant;
20. nullable provider/model failure semantics;
21. provider/model required on success;
22. duration bounds;
23. failure-detail structural bounds;
24. warning tuple, syntax, count, and item bounds;
25. malformed/partial output impossible as success and discarded on failure;
26. no raw-provider-response field;
27. no persistence fields;
28. no tools/functions fields;
29. no Memory fields/imports;
30. no Specialist fields/imports;
31. no business/completion fields;
32. provider-neutral static source/import audit;
33. no Core reverse dependency or semantic modification;
34. Python compile/static import gate; and
35. `git diff --check`.

Focused acceptance requires all tests passing and all 35 gates represented;
there is no pre-authorized fixed pytest function count.

## Dependencies and import direction

Implementation is Python standard-library only. The contract module may use
only local contract definitions and standard-library modules needed for
dataclasses, enums, JSON, math, mapping proxies, collections ABCs, and typing.
No Domain Foundation utility is justified: contract-local validation is
cleaner and avoids semantic coupling.

Allowed conceptual direction is Brain-local consumer → Brain inference
contracts. Prohibited directions/imports include Core Platform → Brain,
inference contracts → Core implementation, and imports involving providers,
SDKs, network/HTTP, persistence/database, Memory, Specialist, tools, or
business domains. No requirements or lockfile change is authorized.

## Required implementation verification

The implementation change must run and record:

- focused Brain contract tests;
- the complete existing Core unit/integration regression suite that does not
  require production/VPS access;
- Domain regressions relevant to dependency direction;
- Stage 8 critical boundary/import and failure-matrix audits;
- Stage 9 source/runtime/privacy prohibited-source audits;
- compile/static import checks;
- a prohibited-field/source audit;
- dependency/import-direction audit; and
- `git diff --check`.

No production, VPS, live-provider, model, network, service, or database test is
required or authorized.
