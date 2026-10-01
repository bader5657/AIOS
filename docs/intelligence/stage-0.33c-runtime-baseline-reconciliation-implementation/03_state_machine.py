"""Pure ledger replay and phase predicates. No filesystem or execution adapter.
All returned actions are proposals, never authorization. The adapter must validate
actual inode/content/custody proofs; a hash chain alone is not authentication.
"""
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re

STATES = ("PREPARED", "OBJECT_DIRECTORIES_CREATED", "OBJECTS_IMPORTED",
          "DIRECTORIES_CREATED", "ANCILLARY_FILES_CREATED", "INDEX_RECONCILED",
          "HEAD_RECONCILED", "VERIFIED")
EVENTS = {"INTENT", "STAGED", "BEFORE", "AFTER", "DONE", "STOP"}
FIELDS = {"attempt_root", "ordinal", "previous_event_sha256", "operation_id", "event",
          "actual_utc", "source_path", "destination_path", "before_identity",
          "after_identity", "content_sha256", "expected_git_oid_if_object",
          "durability_checks", "state", "parent_before_identity", "parent_after_identity",
          "link_count_changes"}
PROOF_FIELDS = {"microstep_id", "program_sha256", "verified", "durable", "evidence"}
IDENTITY_FIELDS = {"dev", "ino", "file_type", "uid", "gid", "mode", "sha256", "nlink"}

class Stop(Exception):
    pass

def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()

def program_hash(program):
    return hashlib.sha256(canonical(program)).hexdigest()

def _pairs(values):
    d = {}
    for k, v in values:
        if k in d:
            raise Stop("duplicate key")
        d[k] = v
    return d

def validation_boundary(function):
    """Pure validation API: malformed external data never escapes as a host error.
    Explicit Stop reasons are preserved; unexpected validation errors have one code.
    This guard does not authorize an append or repair an invalid history.
    """
    def guarded(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Stop:
            raise
        except Exception as exc:
            raise Stop("MALFORMED_INPUT") from exc
    return guarded


@validation_boundary
def validate_chain(blobs, names, operation_ids, attempt_root, *, now_utc):
    require(isinstance(blobs,(list,tuple)) and all(type(b) is bytes for b in blobs), 'ledger bytes type')
    require(isinstance(names,(list,tuple)) and all(type(n) is str for n in names), 'ledger names type')
    require(isinstance(operation_ids,set) and all(type(o) is str for o in operation_ids), 'operation set type')
    require(type(attempt_root) is str and type(now_utc) is str, 'ledger context type')
    if len(blobs) != len(names):
        raise Stop("event/name count")
    prior = None
    previous_time = None
    parsed = []
    for ordinal, (blob, name) in enumerate(zip(blobs, names), 1):
        try:
            x = json.loads(blob.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda v: (_ for _ in ()).throw(Stop("nonfinite")))
            validate_event_types(x)
            if blob != canonical(x):
                raise Stop("closed/canonical event")
            if type(x["ordinal"]) is not int or x["ordinal"] != ordinal or ordinal > 999999:
                raise Stop("ordinal/gap")
            if x["previous_event_sha256"] != prior or x["attempt_root"] != attempt_root:
                raise Stop("chain/attempt mismatch")
            op, event = x["operation_id"], x["event"]
            if not isinstance(op, str) or op not in operation_ids | {"FINAL", "ROLLBACK"}:
                raise Stop("operation")
            if not isinstance(event, str) or event not in EVENTS:
                raise Stop("event")
            if name != f"{ordinal:06d}-{op}-{event}.json":
                raise Stop("filename")
            at = x["actual_utc"]
            if not isinstance(at, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}Z", at):
                raise Stop("time format")
            datetime.strptime(at, "%Y-%m-%dT%H:%M:%S.%fZ")
            if at > now_utc or (previous_time is not None and at < previous_time):
                raise Stop("future/regressed time")
            proof = x["durability_checks"]
            if not isinstance(proof, dict) or set(proof) != PROOF_FIELDS:
                raise Stop("proof shape")
            if not isinstance(proof["microstep_id"], str) or (not isinstance(proof["program_sha256"],str) or not re.fullmatch("[0-9a-f]{64}", proof["program_sha256"])):
                raise Stop("proof binding")
            if type(proof["verified"]) is not bool or type(proof["durable"]) is not bool:
                raise Stop("proof types")
            for field in ("source_path", "destination_path"):
                path = x[field]
                if path is not None and (not isinstance(path, str) or not path.startswith("/") or any(c in ("", ".", "..") for c in path.split("/")[1:])):
                    raise Stop("path encoding")
            validate_payload_shape(x)
            if not isinstance(x["state"], str):
                raise Stop("state type")
        except (ValueError, TypeError, KeyError, UnicodeError) as exc:
            raise Stop("malformed event") from exc
        parsed.append(x)
        prior = hashlib.sha256(blob).hexdigest()
        previous_time = at
    return tuple(parsed)

@dataclass(frozen=True)
class Replay:
    sealed: tuple
    completed: tuple
    active: str | None
    microstep_index: int
    awaiting_after: bool
    awaiting_staged: bool
    halted: bool
    terminal: str | None
    history_digest: str
    namespace: dict
    bindings: dict
    observed: dict | None

@dataclass(frozen=True)
class Choice:
    action: str
    operation_id: str | None = None
    microstep_id: str | None = None
    state: str | None = None

@validation_boundary
def validate_program(program):
    ops = program["operations"]
    expected = ["PREPARE"] + [f"D{i:03}" for i in range(1, 10)] + [f"O{i:03}" for i in range(1, 63)] + ["D010", "F001", "F002", "F003", "M_INDEX", "M_HEAD", "VERIFY"]
    if [o["operation_id"] for o in ops] != expected or program["states"] != list(STATES):
        raise Stop("not the full ordered 79-operation program")
    groups = ["PREPARED"] + ["OBJECT_DIRECTORIES_CREATED"] * 9 + ["OBJECTS_IMPORTED"] * 62 + ["DIRECTORIES_CREATED"] + ["ANCILLARY_FILES_CREATED"] * 3 + ["INDEX_RECONCILED", "HEAD_RECONCILED", "VERIFIED"]
    for op, state in zip(ops, groups):
        steps = op["microsteps"]
        if op["seal_state"] != state or not steps or len({s["id"] for s in steps}) != len(steps):
            raise Stop("operation phase/microsteps")

@validation_boundary
def semantic_replay(program, blobs, names, *, now_utc, evidence_context=None):
    """Derive history only from events; never accepts caller-provided DONE/seal sets.
    Filesystem proof authenticity is separately mandatory. A missing final event is
    an interrupted prefix, never permission to invent preceding history.
    """
    validate_program(program)
    ops = program["operations"]
    events = validate_chain(blobs, names, {o["operation_id"] for o in ops},
                            program["rollback_protocol"]["attempt_root"], now_utc=now_utc)
    evidence = EvidenceReplay(program, evidence_context)
    ph = program_hash(program)
    sealed, completed = [], []
    active = None
    step_index = 0
    before = staged = halted = False
    terminal = None
    for e in events:
        proof = e["durability_checks"]
        if proof["program_sha256"] != ph:
            raise Stop("wrong program digest")
        if halted or terminal:
            raise Stop("event after STOP/terminal")
        evidence.accept(e)
        if e["event"] == "STOP":
            if active is not None:
                stop_target = active
            else:
                state = STATES[len(sealed)]
                required = [o['operation_id'] for o in ops if STATES.index(o['seal_state']) <= len(sealed)]
                stop_target = 'FINAL' if completed == required else ops[len(completed)]['operation_id']
            if e['operation_id'] not in {stop_target, 'ROLLBACK'}:
                raise Stop('STOP operation association')
            if e["state"] != "STOP":
                raise Stop("STOP state")
            halted = True
            continue
        if not proof["verified"] or not proof["durable"]:
            raise Stop("unverified or nondurable event")
        opid, kind = e["operation_id"], e["event"]
        if opid == "ROLLBACK":
            # Rollback uses its own explicitly bound replay stream/plan. Never
            # reinterpret a forward prefix as rollback or restart forward after it.
            if kind != "INTENT" or e["state"] != "ROLLBACK_INTENT" or proof["microstep_id"] != "ENTER_ROLLBACK" or e["source_path"] is not None or e["destination_path"] is not None:
                raise Stop("invalid rollback entry")
            halted = True
            terminal = "ROLLBACK_INTENT"
            continue
        if opid == "FINAL":
            if active is not None or kind != "DONE" or len(sealed) >= len(STATES):
                raise Stop("seal while operation pending/duplicate")
            state = STATES[len(sealed)]
            required = [o["operation_id"] for o in ops if STATES.index(o["seal_state"]) <= len(sealed)]
            if completed != required or e["state"] != state or proof["microstep_id"] != "SEAL:" + state:
                raise Stop("missing/forged/reordered seal")
            if e["source_path"] is not None or e["destination_path"] is not None:
                raise Stop("seal paths")
            sealed.append(state)
            if state == "VERIFIED":
                terminal = "VERIFIED"
            continue
        if len(completed) >= len(ops):
            raise Stop("duplicate completion")
        op = ops[len(completed)]
        phase_index = STATES.index(op["seal_state"])
        if len(sealed) != phase_index or opid != op["operation_id"] or e["state"] != op["seal_state"]:
            raise Stop("missing prior seal/out-of-order operation")
        if kind == "INTENT":
            if active is not None or proof["microstep_id"] != "BEGIN" or e["source_path"] is not None or e["destination_path"] is not None:
                raise Stop("duplicate/out-of-order intent")
            active = opid
            step_index = 0
            before = staged = False
            continue
        if active != opid:
            raise Stop("operation event without INTENT")
        steps = op["microsteps"]
        if kind == "DONE":
            if step_index != len(steps) or before or staged or proof["microstep_id"] != "COMPLETE" or e["source_path"] is not None or e["destination_path"] is not None:
                raise Stop("forged/premature DONE")
            completed.append(opid)
            active = None
            step_index = 0
            continue
        if step_index >= len(steps):
            raise Stop("extra microstep")
        step = steps[step_index]
        if proof["microstep_id"] != step["id"] or e["source_path"] != step["source"] or e["destination_path"] != step["destination"]:
            raise Stop("microstep/path mismatch")
        if kind == "BEFORE":
            if before or staged:
                raise Stop("duplicate/out-of-order BEFORE")
            before = True
        elif kind == "AFTER":
            if not before or staged:
                raise Stop("AFTER without BEFORE")
            before = False
            if step["stage_checkpoint"]:
                staged = True
            else:
                step_index += 1
        elif kind == "STAGED":
            if not staged or before:
                raise Stop("STAGED without durable staging verification")
            staged = False
            step_index += 1
        else:
            raise Stop("illegal event order")
    return Replay(tuple(sealed), tuple(completed), active, step_index, before, staged,
                  halted, terminal, hashlib.sha256(b"".join(blobs)).hexdigest(),
                  evidence.namespace, evidence.bindings, evidence.observed)

@validation_boundary
def next_forward(program, blobs, names, *, now_utc, execution_release_ok,
                 custody_ok, invariant_ok, pending_identity=None, evidence_context=None):
    """Pure choice. invariant_ok is from phase predicate + actual filesystem proof."""
    require(pending_identity is None or type(pending_identity) is str,'pending identity type')
    if any(type(x) is not bool for x in (execution_release_ok, custody_ok, invariant_ok)):
        raise Stop("proof types")
    h = semantic_replay(program, blobs, names, now_utc=now_utc, evidence_context=evidence_context)
    if not custody_ok or not invariant_ok or h.halted:
        raise Stop("custody/invariant/STOP")
    if h.terminal == "VERIFIED":
        return Choice("VERIFY_TERMINAL", state="VERIFIED")
    if not execution_release_ok:
        raise Stop("execution withheld")
    ops = program["operations"]
    if h.active:
        op = ops[len(h.completed)]
        if h.microstep_index == len(op["microsteps"]):
            return Choice("APPEND_DONE_ONLY", h.active, "COMPLETE", op["seal_state"])
        step = op["microsteps"][h.microstep_index]
        if h.awaiting_staged:
            return Choice("APPEND_STAGED_ONLY", h.active, step["id"], op["seal_state"])
        if h.awaiting_after:
            if pending_identity == "PROVEN_BEFORE":
                return Choice("RESUME_EXACT_MICROSTEP", h.active, step["id"], op["seal_state"])
            if pending_identity == "PROVEN_AFTER":
                return Choice("REVERIFY_FSYNC_APPEND_AFTER_ONLY", h.active, step["id"], op["seal_state"])
            raise Stop("ambiguous interrupted microstep")
        return Choice("APPEND_BEFORE_ONLY", h.active, step["id"], op["seal_state"])
    if len(h.sealed) < len(STATES):
        state = STATES[len(h.sealed)]
        required = [o["operation_id"] for o in ops if STATES.index(o["seal_state"]) <= len(h.sealed)]
        if list(h.completed) == required:
            return Choice("VERIFY_BARRIER_THEN_SEAL", "FINAL", "SEAL:" + state, state)
    op = ops[len(h.completed)]
    return Choice("APPEND_INTENT_ONLY", op["operation_id"], "BEGIN", op["seal_state"])


@validation_boundary
def check_namespace(expected, observed, bindings):
    """Exact machine predicate. bindings are authenticated snapshot/STAGED identities.
    nlink is derived from all controlled aliases plus the pinned outside-alias count.
    Observed must enumerate the whole controlled universe, including absent paths.
    """
    require(isinstance(expected,dict) and all(type(k) is str and (v is None or type(v) is str) for k,v in expected.items()),'namespace schema')
    require(isinstance(observed,dict) and all(type(k) is str for k in observed),'observation schema')
    validate_context({'initial_bindings':bindings,'content_hashes':{},'rollback_plan':[]})
    if set(expected) != set(observed):
        raise Stop("missing/extra namespace observation")
    inode_tokens = {}
    aliases = {}
    for token in expected.values():
        if token is not None:
            aliases[token] = aliases.get(token, 0) + 1
    for path, token in expected.items():
        actual = observed[path]
        if token is None:
            if actual is not None:
                raise Stop("unexpected present path")
            continue
        if token not in bindings:
            raise Stop("unbound identity")
        spec = bindings[token]
        if set(spec) != {"identity", "outside_links"}:
            raise Stop("binding shape")
        if not isinstance(actual, dict) or set(actual) != IDENTITY_FIELDS:
            raise Stop("identity shape")
        validate_identity(actual)
        ident = spec["identity"]
        if set(ident) != IDENTITY_FIELDS - {"nlink"}:
            raise Stop("pinned identity shape")
        if ident["file_type"] not in {"regular", "directory"}:
            raise Stop("unsafe pinned type")
        if any(type(ident[k]) is not int or ident[k] < 0 for k in ("dev","ino","uid","gid","mode")) or ident["mode"] > 0o777:
            raise Stop("pinned numeric metadata")
        if (ident["file_type"] == "directory" and ident["sha256"] is not None) or (ident["file_type"] == "regular" and (not isinstance(ident["sha256"], str) or not re.fullmatch("[0-9a-f]{64}", ident["sha256"]))):
            raise Stop("pinned hash")
        inode = (ident["dev"], ident["ino"])
        if inode in inode_tokens and inode_tokens[inode] != token:
            raise Stop("unapproved cross-token hardlink")
        inode_tokens[inode] = token
        for field, value in ident.items():
            if actual[field] != value:
                raise Stop("identity/type/owner/mode/hash mismatch")
        if type(spec["outside_links"]) is not int or spec["outside_links"] < 0:
            raise Stop("outside-link baseline")
        if ident["file_type"] == "directory":
            if aliases[token] != 1:
                raise Stop("directory alias")
            children = [t for child, t in expected.items() if t is not None and child != path
                        and child.rsplit("/", 1)[0] == path.rstrip("/")
                        and bindings[t]["identity"]["file_type"] == "directory"]
            links = spec["outside_links"] + len(children)
        else:
            links = spec["outside_links"] + aliases[token]
        if type(links) is not int or links < 1 or actual["nlink"] != links:
            raise Stop("link count")
    return True


@validation_boundary
def metadata_recovery(direction, live, lock, forward_old, rollback_new):
    forward = {
        ("ORIGINAL", "ABSENT", "ABSENT", "ABSENT"): "LINK_CANDIDATE",
        ("ORIGINAL", "CANDIDATE", "ABSENT", "ABSENT"): "FORWARD_EXCHANGE",
        ("CANDIDATE", "ORIGINAL", "ABSENT", "ABSENT"): "RETAIN_FORWARD_OLD",
        ("CANDIDATE", "ABSENT", "ORIGINAL", "ABSENT"): "VERIFY_FORWARD_COMPLETE",
    }
    reverse = {
        ("CANDIDATE", "ORIGINAL", "ABSENT", "ABSENT"): "RETAIN_FORWARD_OLD",
        ("CANDIDATE", "ABSENT", "ORIGINAL", "ABSENT"): "LINK_ORIGINAL",
        ("CANDIDATE", "ORIGINAL", "ORIGINAL", "ABSENT"): "REVERSE_EXCHANGE",
        ("ORIGINAL", "CANDIDATE", "ORIGINAL", "ABSENT"): "RETAIN_ROLLBACK_NEW",
        ("ORIGINAL", "ABSENT", "ORIGINAL", "CANDIDATE"): "VERIFY_ROLLBACK_COMPLETE",
        ("ORIGINAL", "CANDIDATE", "ABSENT", "ABSENT"): "CANCEL_UNEXCHANGED_LOCK",
        ("ORIGINAL", "ABSENT", "ABSENT", "ABSENT"): "VERIFY_UNTOUCHED",
        ("ORIGINAL", "ABSENT", "ABSENT", "CANDIDATE"): "VERIFY_CANCELLED",
    }
    require(all(type(v) is str for v in (direction,live,lock,forward_old,rollback_new)),'metadata ambiguity')
    table = forward if direction == "FORWARD" else reverse if direction == "ROLLBACK" else None
    if table is None or (live, lock, forward_old, rollback_new) not in table:
        raise Stop("metadata ambiguity")
    return table[live, lock, forward_old, rollback_new]


@validation_boundary
def created_recovery(kind, destination, stage, quarantine, *, staged_proof, published_proof):
    """Labels must come from exact identity predicates, not names or equal hashes."""
    if "FOREIGN" in (destination, stage, quarantine):
        raise Stop("foreign content")
    if kind == "object":
        if quarantine != "ABSENT":
            raise Stop("object quarantine forbidden")
        if destination == stage == "OWNED" and staged_proof:
            return "RETAIN_IMPORTED_OBJECT"
        if destination == "ABSENT" and stage == "OWNED" and staged_proof and not published_proof:
            return "RETAIN_STAGE_OR_RESUME"
        if destination == stage == "ABSENT" and not staged_proof and not published_proof:
            return "UNTOUCHED"
        raise Stop("object ambiguity")
    if kind == "ancillary":
        if destination == stage == "OWNED" and quarantine == "ABSENT" and staged_proof:
            return "QUARANTINE_PROVEN_FILE"
        if destination == "ABSENT" and stage == quarantine == "OWNED" and staged_proof:
            return "VERIFY_QUARANTINED"
    elif kind in ("documentation_directory", "fanout_directory"):
        if destination == "OWNED" and stage == quarantine == "ABSENT" and staged_proof:
            return "RETAIN_FANOUT" if kind == "fanout_directory" else "VERIFY_EMPTY_THEN_QUARANTINE"
        if kind == "documentation_directory" and destination == stage == "ABSENT" and quarantine == "OWNED" and staged_proof:
            return "VERIFY_QUARANTINED"
    else:
        raise Stop("unknown kind")
    if destination == quarantine == "ABSENT" and not published_proof:
        if stage == "OWNED" and staged_proof:
            return "RETAIN_UNPUBLISHED_STAGE"
        if stage == "ABSENT" and not staged_proof:
            return "UNTOUCHED"
    raise Stop("created-artifact ambiguity")


@validation_boundary
def validate_forward_barrier(program, history, state, observed, bindings, git_facts, *, custody_ok):
    if type(custody_ok) is not bool or not custody_ok or type(state) is not str or state not in STATES:
        raise Stop("custody/phase")
    rule = program["phase_barriers"]["forward"][state]
    if history.halted or history.active is not None or list(history.completed) != rule["historical_required_operations"]:
        raise Stop("phase operations/pending")
    expected_prior = rule["historical_required_prior_seals"]
    # Called immediately before seal OR after that exact seal. Never reapply an old
    # namespace predicate after subsequent operations legitimately moved its paths.
    if list(history.sealed) not in (expected_prior, expected_prior + [state]):
        raise Stop("phase history")
    if git_facts != rule["git_predicate"]:
        raise Stop("HEAD/index/worktree/status phase mismatch")
    require(history.namespace == rule["namespace"] and bindings == history.bindings, "forward evidence binding")
    validate_aliases(program, rule["namespace"], observed, bindings)
    return check_namespace(rule["namespace"], observed, bindings)


@validation_boundary
def rollback_namespace(program, entry_namespace, completed):
    """Pure fold; entry_namespace must be bound to replayed forward history and
    authenticated before/after proofs by the adapter, not arbitrary observations.
    """
    require(isinstance(entry_namespace,dict) and all(type(k) is str and (v is None or type(v) is str) for k,v in entry_namespace.items()),'namespace schema')
    require(isinstance(completed,(list,tuple)) and all(type(v) is str for v in completed),'rollback completed type')
    current = dict(entry_namespace)
    lookup = {s["id"]: s for s in program["rollback_occurrences"]}
    for mid in completed:
        if mid not in lookup:
            raise Stop("unknown rollback primitive")
        step = lookup[mid]
        src, dst = step["source"], step["destination"]
        if src not in current or dst not in current or current[src] is None:
            raise Stop("rollback source/namespace")
        if step["subject_operation"] == "D010" and any(t is not None and path.startswith(src+"/") for path,t in current.items()):
            raise Stop("directory not empty")
        if step["primitive"] == "exchange":
            if current[dst] is None:
                raise Stop("exchange absent inode")
            current[src], current[dst] = current[dst], current[src]
        elif step["primitive"] in {"link", "move"}:
            if current[dst] is not None:
                raise Stop("rollback collision")
            current[dst] = current[src]
            if step["primitive"] == "move":
                current[src] = None
        else:
            raise Stop("unapproved rollback primitive")
    return current



def require(condition, reason):
    if not condition:
        raise Stop(reason)


@validation_boundary
def validate_identity(x):
    require(isinstance(x, dict) and set(x) == IDENTITY_FIELDS, 'evidence identity shape')
    require(all(type(x[k]) is int and x[k] >= 0 for k in ('dev','ino','uid','gid','mode','nlink'))
            and x['mode'] <= 0o777 and x['nlink'] >= 1, 'evidence identity metadata')
    require(isinstance(x['file_type'],str) and x['file_type'] in {'regular','directory'}, 'evidence identity type')
    require(x['sha256'] is None if x['file_type']=='directory' else
            isinstance(x['sha256'],str) and re.fullmatch('[0-9a-f]{64}',x['sha256']) is not None,
            'evidence identity hash')


@validation_boundary
def validate_payload_shape(e):
    require(isinstance(e,dict) and set(e)==FIELDS,'closed/canonical event')
    require(type(e['event']) is str,'event string type:event')
    require(isinstance(e['durability_checks'],dict) and set(e['durability_checks'])==PROOF_FIELDS,'proof shape')
    stop=e['event']=='STOP'
    for field in ('before_identity','after_identity','parent_before_identity','parent_after_identity'):
        value=e[field]
        if stop and field in ('after_identity','parent_after_identity'):
            require(value is None,'STOP unknown after evidence')
            continue
        require(isinstance(value,dict),'evidence snapshot shape')
        for path,ident in value.items():
            require(isinstance(path,str) and path.startswith('/') and
                    (path=='/' or all(c not in ('','.','..') for c in path.split('/')[1:])), 'evidence path')
            if ident is not None:validate_identity(ident)
    require(isinstance(e['content_sha256'],dict) and all(isinstance(k,str) and isinstance(v,str)
            and re.fullmatch('[0-9a-f]{64}',v) for k,v in e['content_sha256'].items()),'evidence content hashes')
    obj=e['expected_git_oid_if_object']
    if obj is not None:
        require(isinstance(obj,dict) and set(obj)=={'oid','object_type','raw_bytes','raw_sha256'},'evidence object shape')
        require(isinstance(obj['oid'],str) and re.fullmatch('[0-9a-f]{40}',obj['oid']) is not None and
                isinstance(obj['object_type'],str) and obj['object_type'] in {'blob','tree','commit','tag'} and type(obj['raw_bytes']) is int and obj['raw_bytes']>=0
                and isinstance(obj['raw_sha256'],str) and re.fullmatch('[0-9a-f]{64}',obj['raw_sha256']) is not None,
                'evidence object fields')
    changes=e['link_count_changes']
    if stop:require(changes is None,'STOP unknown link changes')
    else:
        require(isinstance(changes,dict),'evidence link changes shape')
        for token,delta in changes.items():
            require(isinstance(token,str) and isinstance(delta,dict) and set(delta)=={'before','after'} and
                    all(type(v) is int and v>=0 for v in delta.values()),'evidence link delta shape')
    evidence=e['durability_checks']['evidence']
    require(isinstance(evidence,dict) and set(evidence)=={'kind','git_facts','checks','stop_reason','outcome'},'evidence proof shape')
    require(isinstance(evidence['kind'],str) and isinstance(evidence['checks'],list) and
            all(isinstance(v,str) for v in evidence['checks']), 'evidence proof types')
    require(evidence['stop_reason'] is None or type(evidence['stop_reason']) is str,'evidence stop reason type')
    if stop:require(type(evidence['stop_reason']) is str,'evidence stop reason type')
    require(type(evidence['outcome']) is str,'evidence outcome type')
    facts=evidence['git_facts']
    require(facts is None or isinstance(facts,dict),'evidence Git shape')
    if facts is not None:
        forward={'head','index_identity','status_class','worktree_identity'}
        reverse={'head_identity','index_identity','ancillary_present','protected_worktree','status_class'}
        require(set(facts) in (forward,reverse),'evidence Git fields')
        for key,value in facts.items():
            if key=='ancillary_present':
                require(isinstance(value,list) and all(type(v) is str for v in value),'evidence Git list type')
            else:require(type(value) is str,'evidence Git value type')
        if 'head' in facts:require(re.fullmatch('[0-9a-f]{40}',facts['head']) is not None,'evidence Git hash')


@validation_boundary
def validate_event_types(e):
    require(isinstance(e,dict) and set(e)==FIELDS,'closed/canonical event')
    for key in ('attempt_root','operation_id','event','actual_utc','state'):
        require(type(e[key]) is str,'event string type:'+key)
    require(type(e['ordinal']) is int,'ordinal/gap')
    previous=e['previous_event_sha256']
    require(previous is None or (type(previous) is str and re.fullmatch('[0-9a-f]{64}',previous) is not None),'chain hash type')
    for key in ('source_path','destination_path'):
        require(e[key] is None or type(e[key]) is str,'event path type')
    proof=e['durability_checks']
    require(isinstance(proof,dict) and set(proof)==PROOF_FIELDS,'proof shape')
    require(type(proof['microstep_id']) is str and type(proof['program_sha256']) is str,'proof binding type')
    require(re.fullmatch('[0-9a-f]{64}',proof['program_sha256']) is not None,'proof binding')
    require(type(proof['verified']) is bool and type(proof['durable']) is bool,'proof types')
    validate_payload_shape(e)


@validation_boundary
def validate_context(context):
    require(isinstance(context,dict) and set(context)=={'initial_bindings','content_hashes','rollback_plan'},'evidence context required')
    require(isinstance(context['initial_bindings'],dict),'context bindings type')
    for token,binding in context['initial_bindings'].items():
        require(type(token) is str and isinstance(binding,dict) and set(binding)=={'identity','outside_links'},'context binding shape')
        ident=binding['identity']
        require(isinstance(ident,dict) and set(ident)==IDENTITY_FIELDS-{'nlink'},'context identity shape')
        validate_identity({**ident,'nlink':1})
        require(type(binding['outside_links']) is int and binding['outside_links']>=0,'outside-link baseline')
    hashes=context['content_hashes']
    require(isinstance(hashes,dict) and all(type(k) is str and type(v) is str and re.fullmatch('[0-9a-f]{64}',v) is not None for k,v in hashes.items()),'context hashes type')
    plan=context['rollback_plan']
    require(isinstance(plan,list) and all(type(v) is str for v in plan),'context plan type')


@validation_boundary
def validate_aliases(program, namespace, observed, bindings):
    for group in program['baseline_alias_groups']:
        token=group['token']
        require(sorted(path for path,t in namespace.items() if t==token)==group['paths'],'alias membership')
        require(token in bindings and bindings[token]['outside_links']==0,'alias outside links')
        require(bindings[token]['identity']==group['identity'],'alias baseline identity')
        for path in group['paths']:
            actual=observed.get(path)
            require(actual is not None,'missing required alias')
            require((actual['dev'],actual['ino'])==(group['identity']['dev'],group['identity']['ino']), 'missing expected sharing')
            require(actual['nlink']==group['expected_nlink'],'alias link count')
    return True


def observed_parents(observed):
    return {p:v for p,v in observed.items() if v is not None and v['file_type']=='directory'}


def token_counts(namespace, observed):
    return {token:observed[path]['nlink'] for path,token in namespace.items() if token is not None}


def rollback_git(program, namespace, final=False):
    ops={o['operation_id']:o for o in program['operations']}
    return {'head_identity':namespace[ops['M_HEAD']['rule']['path']],
            'index_identity':namespace[ops['M_INDEX']['rule']['path']],
            'ancillary_present':[oid for oid in ('F001','F002','F003') if namespace[ops[oid]['rule']['path']] is not None],
            'protected_worktree':'UNCHANGED_PR306_OVERLAY',
            'status_class':'EXACT_ORIGINAL_TWO_ENTRY_DIRTY' if final else 'EXACT_REPLAYED_TRANSITIONAL_STATUS'}


def rollback_invariants(program, namespace, phase):
    rule=program['phase_barriers']['rollback_predicates'][phase]
    ops={o['operation_id']:o for o in program['operations']}
    for oid in rule['required_restored_metadata']:
        r=ops[oid]['rule']
        require(namespace[r['path']]=='ORIGINAL:'+oid and namespace[r['lock_path']] is None,'original metadata not restored')
    for oid in rule['required_absent_ancillary']:
        require(namespace[ops[oid]['rule']['path']] is None,'ancillary still published')
    if rule['documentation_directory_absent']:
        require(namespace[ops['D010']['rule']['path']] is None,'documentation directory still published')


class EvidenceReplay:
    """No syscalls. Context MUST be independently authenticated by the future adapter.
    Snapshots are observations, not authority: replay derives each namespace effect.
    """
    def __init__(self, program, context):
        require(isinstance(context,dict) and set(context)=={'initial_bindings','content_hashes','rollback_plan'},'evidence context required')
        validate_context(context)
        self.program=program
        self.namespace=dict(program['phase_barriers']['initial_namespace'])
        for s in program['initialization_occurrences']:
            self.namespace[s['destination']]=s['created_token']
        self.bindings={k:{'identity':dict(v['identity']),'outside_links':v['outside_links']} for k,v in context['initial_bindings'].items()}
        require(set(self.bindings)==set(self.namespace.values())-{None},'initial binding membership')
        self.hashes=context['content_hashes']
        contracts=program['created_identity_contracts']
        require(set(self.hashes)=={t for t,c in contracts.items() if c['file_type']=='regular'},'release content membership')
        for token,digest in self.hashes.items():
            require(isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest) is not None,'release content hash')
            pinned=contracts[token]['sha256']
            require(pinned is None or digest==pinned,'release content contradicts program')
        for path,ident in program['baseline_identity_constraints'].items():
            actual=self.bindings[self.namespace[path]]['identity']
            require(all(actual[k]==v for k,v in ident.items() if v is not None),'baseline identity constraint')
        for s in program['initialization_occurrences']:
            self.check_created(s['created_token'],self.bindings[s['created_token']])
        self.observed=None

    def check_created(self, token, binding):
        c=self.program['created_identity_contracts'][token]
        i=binding['identity']
        require(all(i[k]==c[k] for k in ('file_type','uid','gid','mode')) and binding['outside_links']==c['outside_links'],'created metadata contract')
        require(i['sha256']==(self.hashes[token] if i['file_type']=='regular' else None),'created content contract')
        # All controlled mutation paths are on the approved device.
        require(i['dev']==self.bindings[self.namespace['/opt/aios-src/.git']]['identity']['dev'],'created device')

    @validation_boundary
    def accept(self, e):
        validate_event_types(e)
        p=self.program;kind=e['event'];oid=e['operation_id'];proof=e['durability_checks'];mid=proof['microstep_id']
        require(proof['verified'] is True and proof['durable'] is True,'unverified or nondurable event')
        before=e['before_identity'];after=e['after_identity'];prior=dict(self.namespace)
        check_namespace(prior,before,self.bindings)
        validate_aliases(p,prior,before,self.bindings)
        require(self.observed is None or before==self.observed,'evidence snapshot continuity')
        require(e['parent_before_identity']==observed_parents(before),'before parent evidence')
        ops={o['operation_id']:o for o in p['operations']}
        op=ops.get(oid)
        expected_object={k:op['rule'][k] for k in ('oid','object_type','raw_bytes','raw_sha256')} if op and op['kind']=='object' else None
        require(e['expected_git_oid_if_object']==expected_object,'object evidence specification')
        steps={s['id']:s for o in p['operations'] for s in o['microsteps']}
        steps.update({s['id']:s for s in p['rollback_occurrences']})
        if kind in ('BEFORE','AFTER','STAGED'):
            owned={s['id'] for s in (p['rollback_occurrences'] if oid=='ROLLBACK' else op['microsteps'] if op else [])}
            require(mid in owned,'microstep/path mismatch')
        if oid=='ROLLBACK' and kind in ('BEFORE','AFTER'):
            require(mid in {s['id'] for s in p['rollback_occurrences']},'rollback microstep association')
            s=steps[mid];subject=s['subject_operation'];src,dst=s['source'],s['destination']
            if subject in ('M_HEAD','M_INDEX'):
                r=ops[subject]['rule'];live=self.namespace[r['path']];lock=self.namespace[r['lock_path']]
                if mid.endswith('.retain_forward'):
                    valid=live=='CANDIDATE:'+subject and lock=='ORIGINAL:'+subject and self.namespace[dst] is None
                elif mid.endswith('.link_original'):
                    valid=live=='CANDIDATE:'+subject and lock is None and self.namespace[r['quarantine_forward_old']]=='ORIGINAL:'+subject
                elif mid.endswith('.reverse'):
                    valid=live=='CANDIDATE:'+subject and lock=='ORIGINAL:'+subject and self.namespace[r['quarantine_forward_old']]=='ORIGINAL:'+subject
                else:
                    valid=live=='ORIGINAL:'+subject and lock=='CANDIDATE:'+subject and self.namespace[dst] is None
            else:valid=self.namespace[src]=='CREATED:'+subject and self.namespace[dst] is None
            require(valid,'rollback primitive identity precondition')
        if kind=='AFTER':
            require(mid in steps,'evidence unknown microstep')
            s=steps[mid];src,dst=s['source'],s['destination'];primitive=s['primitive']
            if primitive in ('create_file','create_directory'):
                require(self.namespace[dst] is None,'create destination present')
                token=s['created_token'];actual=after.get(dst)
                require(actual is not None,'created identity missing')
                if primitive=='create_file' and src is not None:
                    require(before.get(src) is not None and actual['sha256']==before[src]['sha256'],'copied content evidence')
                require(token not in self.bindings,'duplicate created identity')
                self.bindings[token]={'identity':{k:v for k,v in actual.items() if k!='nlink'},'outside_links':p['created_identity_contracts'][token]['outside_links']}
                self.check_created(token,self.bindings[token]);self.namespace[dst]=token
            elif primitive in ('link','move','exchange'):
                require(src in self.namespace and dst in self.namespace and self.namespace[src] is not None,'effect source absent')
                if primitive=='exchange':
                    require(self.namespace[dst] is not None,'exchange absent inode')
                    self.namespace[src],self.namespace[dst]=self.namespace[dst],self.namespace[src]
                else:
                    require(self.namespace[dst] is None,'effect destination present')
                    if primitive=='move' and self.bindings[self.namespace[src]]['identity']['file_type']=='directory':
                        require(not any(t is not None and path.startswith(src+'/') for path,t in self.namespace.items()),'directory not empty')
                    self.namespace[dst]=self.namespace[src]
                    if primitive=='move':self.namespace[src]=None
            else:
                require(primitive in ('verify','verify_object','verify_graph','verify_clean'),'unknown primitive effect')
        if kind!='STOP':
            check_namespace(self.namespace,after,self.bindings)
            validate_aliases(p,self.namespace,after,self.bindings)
            if kind!='AFTER':require(before==after,'non-effect event changed identity')
            require(e['parent_after_identity']==observed_parents(after),'after parent evidence')
            bc,ac=token_counts(prior,before),token_counts(self.namespace,after)
            changes={t:{'before':bc.get(t,0),'after':ac.get(t,0)} for t in bc.keys()|ac.keys() if bc.get(t,0)!=ac.get(t,0)}
            require(e['link_count_changes']==changes,'link change evidence')
            self.observed=after
        content={t:self.bindings[t]['identity']['sha256'] for t in set(self.namespace.values())-{None} if self.bindings[t]['identity']['file_type']=='regular'}
        require(e['content_sha256']==content,'content evidence specification')
        label={'INTENT':'OPERATION_INTENT','BEFORE':'MICROSTEP_BEFORE','AFTER':'MICROSTEP_AFTER','STAGED':'STAGED_IDENTITY','BARRIER':'ROLLBACK_BARRIER','STOP':'STOP'}.get(kind)
        if kind=='DONE':label='STATE_SEAL' if oid=='FINAL' else 'ROLLBACK_BARRIER' if mid.startswith('BARRIER:') else 'ROLLBACK_PRIMITIVE_COMPLETE' if oid=='ROLLBACK' else 'OPERATION_COMPLETE'
        git=None
        if oid=='FINAL' and e['state'] in STATES:
            rule=p['phase_barriers']['forward'][e['state']]
            require(self.namespace==rule['namespace'],'seal namespace contradiction');git=rule['git_predicate']
        elif oid=='VERIFY' and kind in ('AFTER','DONE'):
            require(self.namespace==p['phase_barriers']['forward']['VERIFIED']['namespace'],'verification namespace contradiction')
            git=p['phase_barriers']['forward']['VERIFIED']['git_predicate']
        elif mid.startswith('BARRIER:') or (oid=='FINAL' and e['state']=='ROLLED_BACK'):
            require(kind=='DONE','barrier event type')
            phase=mid.removeprefix('BARRIER:') if mid.startswith('BARRIER:') else 'PRE_ROLLBACK_SEAL'
            require(phase in p['phase_barriers']['rollback_predicates'],'unknown rollback barrier')
            rollback_invariants(p,self.namespace,phase)
            git=rollback_git(p,self.namespace,phase=='PRE_ROLLBACK_SEAL')
        ev=proof['evidence']
        require(ev['kind']==label,'evidence kind association')
        if kind=='STOP':
            require(mid=='STOP' and e['state']=='STOP' and e['source_path'] is None and e['destination_path'] is None,'STOP association')
            require(ev['stop_reason'] in {'IO_FAILURE','IDENTITY_MISMATCH','CUSTODY_LOST','REVOKED','VERIFICATION_FAILED'} and ev['outcome']=='UNKNOWN_RETAIN' and ev['checks']==[] and ev['git_facts'] is None,'STOP evidence')
        else:
            require(ev['checks']==[label,mid,e['state']] and ev['stop_reason'] is None and ev['outcome']=='PROVEN','evidence checks association')
            require(ev['git_facts']==git,'Git evidence contradiction')

@validation_boundary
def rollback_schedule(program, plan):
    allowed={s['id']:s for s in program['rollback_occurrences']}
    require(isinstance(plan,list) and all(isinstance(s,str) and s in allowed for s in plan)
            and len(set(plan))==len(plan),'unknown rollback plan')
    require(plan==sorted(plan,key=list(allowed).index),'HEAD/index/ancillary rollback order')
    schedule=[('DONE','BARRIER:ENTER')]
    for subject,phase in zip(['M_HEAD','M_INDEX','F003','F002','F001','D010'],
                             ['RESTORE_HEAD','RESTORE_INDEX','UNDO_F003','UNDO_F002','UNDO_F001','UNDO_D010']):
        for mid in plan:
            if allowed[mid]['subject_operation']==subject:
                schedule.extend((kind,mid) for kind in ('BEFORE','AFTER','DONE'))
        schedule.append(('DONE','BARRIER:'+phase))
    schedule.extend([('DONE','BARRIER:PRE_ROLLBACK_SEAL'),('DONE','SEAL:ROLLED_BACK')])
    return schedule


@validation_boundary
def semantic_rollback_replay(program, blobs, names, *, now_utc, rollback_plan, evidence_context=None):
    validate_context(evidence_context)
    require(isinstance(rollback_plan,list) and all(type(v) is str for v in rollback_plan),'unknown rollback plan')
    require(rollback_plan==evidence_context['rollback_plan'],'rollback plan binding')
    schedule=rollback_schedule(program,rollback_plan)
    ops={o['operation_id'] for o in program['operations']}
    events=validate_chain(blobs,names,ops,program['rollback_protocol']['attempt_root'],now_utc=now_utc)
    entries=[i for i,e in enumerate(events) if e['operation_id']=='ROLLBACK' and e['event']=='INTENT']
    require(len(entries)==1,'missing/duplicate rollback entry')
    cut=entries[0]
    history=semantic_replay(program,blobs[:cut+1],names[:cut+1],now_utc=now_utc,evidence_context=evidence_context)
    require(history.terminal=='ROLLBACK_INTENT','rollback entry')
    evidence=EvidenceReplay(program,evidence_context)
    evidence.namespace=dict(history.namespace);evidence.bindings=history.bindings.copy();evidence.observed=history.observed
    completed=[];barriers=[];position=0;terminal=None
    lookup={s['id']:s for s in program['rollback_occurrences']}
    for e in events[cut+1:]:
        require(terminal is None,'event after rollback terminal')
        require(e['durability_checks']['program_sha256']==program_hash(program),'wrong program digest')
        if e['event']=='STOP':
            stop_target='FINAL' if schedule[position][1]=='SEAL:ROLLED_BACK' else 'ROLLBACK'
            require(e['operation_id']==stop_target,'STOP operation association')
            evidence.accept(e)
            raise Stop('rollback STOP')
        require(position<len(schedule),'extra rollback operation')
        kind,mid=schedule[position]
        require(e['event']==kind and e['durability_checks']['microstep_id']==mid,'rollback event order')
        seal=mid=='SEAL:ROLLED_BACK'
        require(e['operation_id']==('FINAL' if seal else 'ROLLBACK') and e['state']==('ROLLED_BACK' if seal else 'ROLLBACK_INTENT'),'rollback state association')
        s=lookup.get(mid)
        require(e['source_path']==(s['source'] if s else None) and e['destination_path']==(s['destination'] if s else None),'rollback path mismatch')
        evidence.accept(e)
        if seal:terminal='ROLLED_BACK'
        elif mid.startswith('BARRIER:'):barriers.append(mid.removeprefix('BARRIER:'))
        elif kind=='DONE':completed.append(mid)
        position+=1
    return {'forward_history':history,'completed':tuple(completed),'barriers':tuple(barriers),
            'next_event':schedule[position][0] if position<len(schedule) else None,
            'next_microstep':schedule[position][1] if position<len(schedule) else None,
            'terminal':terminal,'namespace':evidence.namespace,'bindings':evidence.bindings,'observed':evidence.observed}


@validation_boundary
def validate_rollback_barrier(program, replayed, phase, prior_barriers, plan,
                              entry_namespace, observed, bindings, git_facts,
                              *, custody_ok, entry_proof_ok):
    rules=program['phase_barriers']['rollback_predicates']
    require(type(phase) is str and phase in rules and custody_ok is True and entry_proof_ok is True,'rollback phase/custody/entry proof')
    rule=rules[phase];expected_prior=rule['required_prior_barriers']
    # Prior phase names alone never establish evidence: compare reconstructed records.
    require(list(prior_barriers)==expected_prior and list(replayed['barriers'])==expected_prior,'rollback barrier history')
    post=phase=='POST_ROLLBACK_TERMINAL'
    require(replayed['terminal']==('ROLLED_BACK' if post else None),'rollback terminal phase')
    if not post:
        require(replayed['next_event']=='DONE' and replayed['next_microstep']=='BARRIER:'+phase,'rollback pending phase')
    require(entry_namespace==replayed['forward_history'].namespace,'rollback entry namespace binding')
    require(replayed['namespace']==rollback_namespace(program,entry_namespace,replayed['completed']),'rollback namespace fold')
    rollback_invariants(program,replayed['namespace'],phase)
    require(git_facts==rollback_git(program,replayed['namespace'],phase in ('PRE_ROLLBACK_SEAL','POST_ROLLBACK_TERMINAL')),'rollback Git/worktree facts')
    require(bindings==replayed['bindings'],'rollback identity binding')
    validate_aliases(program,replayed['namespace'],observed,bindings)
    return check_namespace(replayed['namespace'],observed,bindings)


@validation_boundary
def verify_terminal(program, history, observed, bindings, git_facts, *, custody_ok):
    require(custody_ok is True,'terminal custody')
    if isinstance(history,Replay):
        require(history.terminal=='VERIFIED','terminal state')
        return validate_forward_barrier(program,history,'VERIFIED',observed,bindings,git_facts,custody_ok=True)
    require(history['terminal']=='ROLLED_BACK','terminal state')
    require(history['barriers']==tuple(program['phase_barriers']['rollback_machine_contract']['phase_order'][:-1]),'terminal rollback barriers')
    rollback_invariants(program,history['namespace'],'POST_ROLLBACK_TERMINAL')
    require(bindings==history['bindings'],'terminal identity binding')
    require(git_facts==rollback_git(program,history['namespace'],True),'terminal Git contradiction')
    validate_aliases(program,history['namespace'],observed,bindings)
    return check_namespace(history['namespace'],observed,bindings)


@validation_boundary
def metadata_rollback_decision(program, history, subject):
    """Pure recovery decision from semantically replayed, checked observations.
    Returns remaining primitive IDs and original-live target, never execution authority.
    """
    require(type(subject) is str and subject in ('M_HEAD','M_INDEX'),'metadata subject')
    ns=history.namespace if isinstance(history,Replay) else history['namespace']
    bindings=history.bindings if isinstance(history,Replay) else history['bindings']
    observed=history.observed if isinstance(history,Replay) else history['observed']
    check_namespace(ns,observed,bindings)
    rule=next(o['rule'] for o in program['operations'] if o['operation_id']==subject)
    def label(path):
        token=ns[path]
        return 'ABSENT' if token is None else 'ORIGINAL' if token=='ORIGINAL:'+subject else 'CANDIDATE' if token=='CANDIDATE:'+subject else 'FOREIGN'
    action=metadata_recovery('ROLLBACK',*[label(rule[k]) for k in ('path','lock_path','quarantine_forward_old','quarantine_rollback_new')])
    remaining={
        'RETAIN_FORWARD_OLD':['retain_forward','link_original','reverse','retain_candidate'],
        'LINK_ORIGINAL':['link_original','reverse','retain_candidate'],
        'REVERSE_EXCHANGE':['reverse','retain_candidate'],
        'RETAIN_ROLLBACK_NEW':['retain_candidate'],
        'CANCEL_UNEXCHANGED_LOCK':['retain_candidate'],
        'VERIFY_ROLLBACK_COMPLETE':[], 'VERIFY_UNTOUCHED':[], 'VERIFY_CANCELLED':[]}[action]
    return {'action':action,'remaining':tuple('ROLLBACK.'+subject+'.'+x for x in remaining),
            'target':{rule['path']:'ORIGINAL:'+subject,rule['lock_path']:None}}
