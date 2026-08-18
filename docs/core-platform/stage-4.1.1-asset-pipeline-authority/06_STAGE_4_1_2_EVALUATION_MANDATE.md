# Stage 4.1.2 Historical Implementation Evaluation Mandate

Stage 4.1.2 must decide the disposition of historical commit
`9d1288cca4b47d6fca963a8bff16041599b5e5c4` and these evidence paths:

- `core/pipeline/__init__.py`;
- `core/pipeline/asset_pipeline.py`;
- `core/pipeline/state.py`;
- `tests/unit/pipeline/__init__.py`; and
- `tests/unit/pipeline/test_asset_pipeline.py`.

It must record exactly one approved disposition, such as `ADAPT`, `REPLACE`, or
`REJECT`, with line-by-line evidence against this active contract. The earlier
Stage 1.2.1 `ADAPT` finding is evidence and a constraint against blind reuse;
it is not automatic Stage 4 acceptance.

At minimum Stage 4.1.2 must evaluate:

- signature compatibility with the approved Request Context boundary;
- preservation of recognized media identity without reclassification;
- storage, metadata, and Document Manifest authority separation;
- compatibility with all accepted Stage 3 input variants and paths;
- removal/rejection of speculative six-state semantics;
- terminal result necessity and minimum shape;
- failure-gate conformance and absence of false success;
- absence of duplicate behavior beyond authority;
- dependency directions, including Storage → App regression risk;
- Registry/PostgreSQL absence;
- historical test sufficiency; and
- the smallest candidate runtime/test file set for later approval.

Stage 4.1.2 is review/disposition work only. It grants no implementation,
restoration, merge, schema, dependency, or test-change authority.
