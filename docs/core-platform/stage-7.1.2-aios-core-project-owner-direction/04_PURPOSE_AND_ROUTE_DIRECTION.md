# Purpose and Route Direction

AIOS Core is the bounded coordination/routing layer between Event Engine and
the AIOS Brain boundary. For one accepted bounded input, it determines the next
authorized downstream handoff category and returns a bounded routing
disposition.

`Route` means a bounded coordination decision for that handoff. It is not
network/HTTP/broker routing, Specialist Router behavior, business-rule routing,
LLM reasoning, workflow execution, job scheduling, or Brain invocation.
