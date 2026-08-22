# Formal Exclusion Ledger

## Nine-candidate disposition

| Candidate | 10.1.1 source | 10.1.2 classification | Reason |
|---|---|---|---|
| Brain execution/reasoning | CP-TRACE-074/076 | `LATER_STAGE_CAPABILITY / FORMALLY_EXCLUDED` | Core ends at `AIOS_BRAIN_BOUNDARY`; no Brain execution is required or claimed |
| Intelligence/LLM | CP-TRACE-077/100 | `LATER_STAGE_CAPABILITY / FORMALLY_EXCLUDED` | Frozen plan expressly excludes Intelligence from Core Platform |
| Memory/Knowledge runtime | CP-TRACE-076/100 | `LATER_STAGE_CAPABILITY / FORMALLY_EXCLUDED` | Blueprint places it inside/downstream of Brain |
| Specialist Router/Specialists | CP-TRACE-076/100 | `LATER_STAGE_CAPABILITY / FORMALLY_EXCLUDED` | Downstream specialist capability belongs to later phases |
| Business workflow/runtime | CP-TRACE-003/077/100 | `LATER_STAGE_CAPABILITY / FORMALLY_EXCLUDED` | Readiness acknowledgement is not business completion |
| Autonomous automation | CP-TRACE-098/100 | `LATER_STAGE_CAPABILITY / FORMALLY_EXCLUDED` | Only accepted systemd lifecycle automation is current |
| n8n/Hermes/OpenClaw/Ollama runtime | 10.1.1 possible-exclusion ledger | `FORMALLY_EXCLUDED — UNAPPROVED EXTERNAL/LATER RUNTIME` | No current Core authority or dependency |
| Broker/queue/distributed Event infrastructure | CP-TRACE-068 | `FORMALLY_EXCLUDED — UNAPPROVED INFRASTRUCTURE` | Accepted Event Engine is bounded and in-process |
| Generalized retry/deduplication/compensation | CP-TRACE-053/054/069/083 | `INCLUDED_REQUIREMENT_SATISFIED_BY_NONE_SEMANTICS` | Explicit absence is accepted behavior, not deferred implementation |

All nine candidates are dispositioned. Eight enter the formal ledger; the
ninth remains an Included negative/none semantic.

| Exclusion ID | Item | Authority | Authority section | Rationale | Future/later owner | Current implementation dependency | Current capability claim | Completion impact | Final disposition |
|---|---|---|---|---|---|---|---|---|---|
| CP-EX-001 | Brain execution/reasoning | Blueprint; Frozen Roadmap; EP | Pipeline after Core; Core boundary | Milestone stops at readiness | Intelligence/Brain phase | None; boundary marker only | Not active | None | FORMALLY_EXCLUDED / LATER_STAGE_CAPABILITY |
| CP-EX-002 | Intelligence/LLM runtime | Frozen Roadmap; EP | Intelligence after Core | Not Core capability | Intelligence phase | None | Later/unverified | None | FORMALLY_EXCLUDED / LATER_STAGE_CAPABILITY |
| CP-EX-003 | Memory/Knowledge runtime | Blueprint; Roadmap; EP | AIOS Brain | Downstream Brain capability | Intelligence/Memory phase | None | Later/unverified | None | FORMALLY_EXCLUDED / LATER_STAGE_CAPABILITY |
| CP-EX-004 | Specialist Router/Specialists | Blueprint; Roadmap; EP | Pipeline after Brain | Downstream capability | Intelligence/Business Capability | None | Later/unverified | None | FORMALLY_EXCLUDED / LATER_STAGE_CAPABILITY |
| CP-EX-005 | Business workflow/runtime | Roadmap; EP | Business Capability | Not transport readiness | Business Capability | None | Roadmap/unverified | None | FORMALLY_EXCLUDED / LATER_STAGE_CAPABILITY |
| CP-EX-006 | Broader autonomous automation | Blueprint; Roadmap; Stage 9.3.1 | Future capability boundary | systemd is not business automation | Later business/automation authority | None | Unverified beyond service lifecycle | None | FORMALLY_EXCLUDED / LATER_STAGE_CAPABILITY |
| CP-EX-007 | n8n/Hermes/OpenClaw/Ollama runtime | EP; Stage 8/9 audits | Core-only/no-new-infrastructure | No authority/dependency | Separate external/Intelligence work | None | Not claimed | None | FORMALLY_EXCLUDED / UNAPPROVED EXTERNAL-LATER RUNTIME |
| CP-EX-008 | Broker/queue/distributed Event infrastructure | EP; Stage 6/8 closures | In-process Event boundary | Current contract has no broker/queue/ledger | Separate future architecture | None; in-memory handlers | Not claimed | None | FORMALLY_EXCLUDED / UNAPPROVED INFRASTRUCTURE |

`FORMALLY_EXCLUDED = 8`

No exclusion removes an Included Scope requirement or supplies a false pass.
