# Historical Separation Evidence

The implementation is fresh and contract-first. It restores none of the
historical conversation engine, command router, specialist router,
orchestration logic, business routing, LLM behavior, session state, persistence,
or historical routing APIs.

The AIOS Core package contains only `__init__.py` and `core.py`; its approved
public export surface is limited to `AIOSCore`, `CoreRouteTarget`,
`CoreRouteFailureCode`, and `CoreRouteResult`.
