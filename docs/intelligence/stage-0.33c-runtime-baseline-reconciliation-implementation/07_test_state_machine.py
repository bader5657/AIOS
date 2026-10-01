"""PREPARED / NOT RUN. Pure synthetic observations derived from the approved program.
No filesystem adapter, runtime reads, subprocess, authority, or test execution here.
"""
import copy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('reconciliation_model',ROOT/'03_state_machine.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
P=json.loads((ROOT/'01_OPERATION_PROGRAM.json').read_bytes())
OPS=P['operations'];PH=m.program_hash(P)
AT='2026-09-30T00:00:00.000000Z';NOW='2030-01-01T00:00:00.000000Z'
PHASES=P['phase_barriers']['rollback_machine_contract']['phase_order']
ROWS=P['metadata_recovery_rows']
INVALID=[(d,*v) for d in ('FORWARD','ROLLBACK') for v in itertools.product(('ORIGINAL','CANDIDATE','ABSENT','FOREIGN'),repeat=4)
         if not any((r['direction'],r['live'],r['lock'],r['forward_old'],r['rollback_new'])==(d,*v) for r in ROWS)]

def digest(value):return hashlib.sha256(value.encode()).hexdigest()

def fixture():
    """Use baseline device/inode/hash/owner/type and actual approved alias groups.
    Fill ONLY unprovided preflight values synthetically; never rewrite approved pins.
    """
    ns=dict(P['phase_barriers']['initial_namespace'])
    for s in P['initialization_occurrences']:ns[s['destination']]=s['created_token']
    bindings={}
    constraints=P['baseline_identity_constraints']
    for path,token in ns.items():
        if token is None or token in bindings:continue
        ident={'dev':2049,'ino':10000000+len(bindings),'uid':1000,'gid':1000,'mode':0o755,
               'file_type':'directory' if token.startswith('BASE:') else 'regular','sha256':None}
        ident.update({k:v for k,v in constraints.get(path,{}).items() if v is not None})
        contract=P['created_identity_contracts'].get(token)
        if contract:ident.update({k:v for k,v in contract.items() if k!='outside_links'})
        if ident['file_type']=='regular' and ident['sha256'] is None:ident['sha256']=digest(token)
        bindings[token]={'identity':ident,'outside_links':2 if ident['file_type']=='directory' else 0}
    hashes={t:c['sha256'] or digest(t) for t,c in P['created_identity_contracts'].items() if c['file_type']=='regular'}
    for operation in OPS:
        for step in operation['microsteps']:
            if step['primitive']=='create_file' and step['source'] is not None:
                hashes[step['created_token']]=bindings[ns[step['source']]]['identity']['sha256']
    context={'initial_bindings':copy.deepcopy(bindings),'content_hashes':hashes,'rollback_plan':[]}
    return ns,bindings,context

def observe(ns,bindings):
    result={}
    for path,t in ns.items():
        if t is None:result[path]=None;continue
        b=bindings[t];i=dict(b['identity'])
        count=sum(v==t for v in ns.values()) if i['file_type']=='regular' else sum(v is not None and q!=path and q.rsplit('/',1)[0]==path.rstrip('/') and bindings[v]['identity']['file_type']=='directory' for q,v in ns.items())
        result[path]={**i,'nlink':b['outside_links']+count}
    return result

def effect(ns,bindings,step,context):
    """Fixture oracle uses declared primitive semantics, independently of replay code."""
    ns=dict(ns);bindings=copy.deepcopy(bindings);src,dst=step['source'],step['destination'];primitive=step['primitive']
    if primitive.startswith('create_'):
        t=step['created_token'];c=P['created_identity_contracts'][t]
        ident={k:v for k,v in c.items() if k!='outside_links'}
        ident.update(dev=2049,ino=20000000+len(bindings),sha256=context['content_hashes'].get(t))
        bindings[t]={'identity':ident,'outside_links':c['outside_links']};ns[dst]=t
    elif primitive=='exchange':ns[src],ns[dst]=ns[dst],ns[src]
    elif primitive in ('link','move'):
        ns[dst]=ns[src]
        if primitive=='move':ns[src]=None
    return ns,bindings

def git_rollback(ns,final=False):
    return {'head_identity':ns['/opt/aios-src/.git/HEAD'],'index_identity':ns['/opt/aios-src/.git/index'],
            'ancillary_present':[o['operation_id'] for o in OPS if o['kind']=='ancillary' and ns[o['rule']['path']] is not None],
            'protected_worktree':'UNCHANGED_PR306_OVERLAY','status_class':'EXACT_ORIGINAL_TWO_ENTRY_DIRTY' if final else 'EXACT_REPLAYED_TRANSITIONAL_STATUS'}

def event(oid,kind,mid,state,ns,bindings,context,step=None):
    before=observe(ns,bindings);old=dict(ns)
    if kind=='AFTER':ns,bindings=effect(ns,bindings,step,context)
    after=observe(ns,bindings)
    label={'INTENT':'OPERATION_INTENT','BEFORE':'MICROSTEP_BEFORE','AFTER':'MICROSTEP_AFTER','STAGED':'STAGED_IDENTITY','BARRIER':'ROLLBACK_BARRIER','STOP':'STOP'}.get(kind)
    if kind=='DONE':label='STATE_SEAL' if oid=='FINAL' else 'ROLLBACK_BARRIER' if mid.startswith('BARRIER:') else 'ROLLBACK_PRIMITIVE_COMPLETE' if oid=='ROLLBACK' else 'OPERATION_COMPLETE'
    git=None
    if oid=='FINAL' and state in m.STATES:git=P['phase_barriers']['forward'][state]['git_predicate']
    elif oid=='VERIFY' and kind in ('AFTER','DONE'):git=P['phase_barriers']['forward']['VERIFIED']['git_predicate']
    elif mid.startswith('BARRIER:') or (oid=='FINAL' and state=='ROLLED_BACK'):git=git_rollback(ns,mid in ('BARRIER:PRE_ROLLBACK_SEAL','SEAL:ROLLED_BACK'))
    bc={t:before[path]['nlink'] for path,t in old.items() if t};ac={t:after[path]['nlink'] for path,t in ns.items() if t}
    op=next((o for o in OPS if o['operation_id']==oid),None)
    obj={k:op['rule'][k] for k in ('oid','object_type','raw_bytes','raw_sha256')} if op and op['kind']=='object' else None
    stop=kind=='STOP'
    ev={'attempt_root':P['rollback_protocol']['attempt_root'],'ordinal':0,'previous_event_sha256':None,'operation_id':oid,'event':kind,'actual_utc':AT,
        'source_path':step['source'] if step else None,'destination_path':step['destination'] if step else None,
        'before_identity':before,'after_identity':None if stop else after,'parent_before_identity':{q:v for q,v in before.items() if v and v['file_type']=='directory'},
        'parent_after_identity':None if stop else {q:v for q,v in after.items() if v and v['file_type']=='directory'},
        'content_sha256':{t:bindings[t]['identity']['sha256'] for t in set(ns.values())-{None} if bindings[t]['identity']['file_type']=='regular'},
        'expected_git_oid_if_object':obj,'link_count_changes':None if stop else {t:{'before':bc.get(t,0),'after':ac.get(t,0)} for t in bc.keys()|ac.keys() if bc.get(t,0)!=ac.get(t,0)},'state':state,
        'durability_checks':{'microstep_id':mid,'program_sha256':PH,'verified':True,'durable':True,
         'evidence':{'kind':label,'git_facts':git,'checks':[] if stop else [label,mid,state],'stop_reason':'VERIFICATION_FAILED' if stop else None,'outcome':'UNKNOWN_RETAIN' if stop else 'PROVEN'}}}
    return ev,ns,bindings

def encode(events):
    blobs=[];names=[];previous=None
    for n,source in enumerate(events,1):
        e={**source,'ordinal':n,'previous_event_sha256':previous};blob=m.canonical(e)
        blobs.append(blob);names.append(f"{n:06d}-{e['operation_id']}-{e['event']}.json");previous=hashlib.sha256(blob).hexdigest()
    return blobs,names

def build():
    ns,b,ctx=fixture();events=[];done={};seals={};maps={}
    def emit(oid,kind,mid,state,step=None):
        nonlocal ns,b
        e,ns,b=event(oid,kind,mid,state,ns,b,ctx,step);events.append(e)
    for i,o in enumerate(OPS):
        oid,state=o['operation_id'],o['seal_state'];emit(oid,'INTENT','BEGIN',state)
        for s in o['microsteps']:
            for k in ['BEFORE','AFTER']+(['STAGED'] if s['stage_checkpoint'] else []):emit(oid,k,s['id'],state,s)
        emit(oid,'DONE','COMPLETE',state);done[oid]=len(events)
        if i==len(OPS)-1 or OPS[i+1]['seal_state']!=state:
            emit('FINAL','DONE','SEAL:'+state,state);seals[state]=len(events);maps[state]=(dict(ns),copy.deepcopy(b))
    return events,done,seals,maps,ctx

EVENTS,DONE,SEALS,MAPS,CTX=build()
BOUNDARIES=[i+1 for i,e in enumerate(EVENTS) if e['event'] in ('AFTER','STAGED','DONE')]
BEFORES=[i+1 for i,e in enumerate(EVENTS) if e['event']=='BEFORE']

def replay(events,ctx=CTX):
    b,n=encode(events)
    m.validate_chain(b,n,{o['operation_id'] for o in OPS},P['rollback_protocol']['attempt_root'],now_utc=NOW)
    return m.semantic_replay(P,b,n,now_utc=NOW,evidence_context=ctx)

def choice(events,**kwargs):
    b,n=encode(events);options=dict(now_utc=NOW,evidence_context=CTX,execution_release_ok=True,custody_ok=True,invariant_ok=True);options.update(kwargs)
    return m.next_forward(P,b,n,**options)

def stopped(reason,call):
    with pytest.raises(m.Stop) as error:call()
    assert str(error.value)==reason

def expected_choice(cut):
    if cut==len(EVENTS):return ('VERIFY_TERMINAL',None,None,'VERIFIED')
    nxt=EVENTS[cut];oid=nxt['operation_id'];mid=nxt['durability_checks']['microstep_id'];state=nxt['state']
    action='VERIFY_BARRIER_THEN_SEAL' if oid=='FINAL' else {'INTENT':'APPEND_INTENT_ONLY','BEFORE':'APPEND_BEFORE_ONLY','STAGED':'APPEND_STAGED_ONLY','DONE':'APPEND_DONE_ONLY'}[nxt['event']]
    return action,oid,mid,state

def as_tuple(c):return c.action,c.operation_id,c.microstep_id,c.state

def test_full_real_program():
    h=replay(EVENTS)
    assert h.completed==tuple(o['operation_id'] for o in OPS) and len(h.completed)==79
    assert h.sealed==m.STATES and h.active is None and h.terminal=='VERIFIED'
    assert h.namespace==P['phase_barriers']['forward']['VERIFIED']['namespace']

@pytest.mark.parametrize('cut',BOUNDARIES)
def test_exact_retry_action_at_every_completion(cut):
    assert as_tuple(choice(EVENTS[:cut]))==expected_choice(cut)
    h=replay(EVENTS[:cut]);assert h.completed==tuple(o['operation_id'] for o in OPS if DONE[o['operation_id']]<=cut)
    assert h.sealed==tuple(s for s in m.STATES if SEALS[s]<=cut)

@pytest.mark.parametrize('cut',BEFORES)
def test_pending_effect_classification(cut):
    e=EVENTS[cut-1];mid=e['durability_checks']['microstep_id']
    stopped('ambiguous interrupted microstep',lambda:choice(EVENTS[:cut]))
    for classification,action in [('PROVEN_BEFORE','RESUME_EXACT_MICROSTEP'),('PROVEN_AFTER','REVERIFY_FSYNC_APPEND_AFTER_ONLY')]:
        assert as_tuple(choice(EVENTS[:cut],pending_identity=classification))==(action,e['operation_id'],mid,e['state'])

@pytest.mark.parametrize('state',list(m.STATES))
def test_barrier_and_state_retry(state):
    h=replay(EVENTS[:SEALS[state]]);ns,b=MAPS[state]
    assert h.namespace==ns==P['phase_barriers']['forward'][state]['namespace']
    assert m.validate_forward_barrier(P,h,state,observe(ns,b),b,P['phase_barriers']['forward'][state]['git_predicate'],custody_ok=True) is True
    assert as_tuple(choice(EVENTS[:SEALS[state]]))==expected_choice(SEALS[state])

@pytest.mark.parametrize('group',P['baseline_alias_groups'])
def test_baseline_alias_membership_and_linkcount(group):
    h=replay(EVENTS[:SEALS['PREPARED']]);obs=h.observed
    assert [q for q,t in h.namespace.items() if t==group['token']]==group['paths']
    assert all(obs[q]['ino']==group['identity']['ino'] and obs[q]['dev']==group['identity']['dev'] and obs[q]['nlink']==len(group['paths']) for q in group['paths'])
    assert m.validate_aliases(P,h.namespace,obs,h.bindings) is True

@pytest.mark.parametrize('group',P['baseline_alias_groups'])
@pytest.mark.parametrize('fault',['split','missing','extra','nlink','hash','owner','group','mode'])
def test_alias_corruption_stops(group,fault):
    ns,b,_=fixture();obs=observe(ns,b);q=group['paths'][0]
    reason='identity/type/owner/mode/hash mismatch'
    if fault=='split':obs[q]['ino']+=1;reason='missing expected sharing'
    elif fault=='missing':obs[q]=None;reason='missing required alias'
    elif fault=='extra':ns['/unexpected']=group['token'];obs['/unexpected']=dict(obs[q]);reason='alias membership'
    elif fault=='nlink':obs[q]['nlink']+=1;reason='alias link count'
    else:obs[q][{'hash':'sha256','owner':'uid','group':'gid','mode':'mode'}[fault]]=digest('bad') if fault=='hash' else obs[q][{'owner':'uid','group':'gid','mode':'mode'}[fault]]+1
    def check():m.validate_aliases(P,ns,obs,b);m.check_namespace(ns,obs,b)
    stopped(reason,check)

def test_unapproved_inode_sharing_stops():
    ns,b,_=fixture();tokens=[t for t in b if t.startswith('BASE:')][:2]
    b[tokens[1]]['identity'].update(dev=b[tokens[0]]['identity']['dev'],ino=b[tokens[0]]['identity']['ino'])
    stopped('unapproved cross-token hardlink',lambda:m.check_namespace(ns,observe(ns,b),b))

@pytest.mark.parametrize('state',list(m.STATES))
@pytest.mark.parametrize('field',['ino','dev','uid','gid','mode','sha256','nlink','file_type'])
def test_each_barrier_metadata_drift(state,field):
    h=replay(EVENTS[:SEALS[state]]);obs=copy.deepcopy(h.observed);q='/opt/aios-src/.git/HEAD'
    if field=='sha256':obs[q][field]=digest('bad')
    elif field=='file_type':obs[q][field]='symlink'
    else:obs[q][field]+=1
    reason='evidence identity type' if field=='file_type' else 'link count' if field=='nlink' else 'identity/type/owner/mode/hash mismatch'
    stopped(reason,lambda:m.validate_forward_barrier(P,h,state,obs,h.bindings,P['phase_barriers']['forward'][state]['git_predicate'],custody_ok=True))

@pytest.mark.parametrize('state',list(m.STATES[:-1]))
def test_missing_seal_blocks_next_operation(state):
    events=list(EVENTS);del events[SEALS[state]-1]
    stopped('missing prior seal/out-of-order operation',lambda:replay(events))

@pytest.mark.parametrize('state',list(m.STATES))
def test_duplicate_seal(state):
    events=list(EVENTS[:SEALS[state]]);events.append(events[-1])
    reason='event after STOP/terminal' if state=='VERIFIED' else 'seal namespace contradiction'
    # The duplicated seal map equals its own phase; order is rejected by replay.
    if state!='VERIFIED':reason='missing/forged/reordered seal'
    stopped(reason,lambda:replay(events))

@pytest.mark.parametrize('oid',[o['operation_id'] for o in OPS])
def test_missing_operation_completion(oid):
    events=list(EVENTS);del events[DONE[oid]-1]
    reason='seal while operation pending/duplicate' if oid in ('PREPARE','D009','O062','D010','F003','M_INDEX','M_HEAD','VERIFY') else 'missing prior seal/out-of-order operation'
    stopped(reason,lambda:replay(events))

@pytest.mark.parametrize('oid',[o['operation_id'] for o in OPS])
def test_duplicate_completion(oid):
    events=list(EVENTS[:DONE[oid]]);events.append(events[-1])
    stopped('duplicate completion' if oid=='VERIFY' else 'missing prior seal/out-of-order operation',lambda:replay(events))

@pytest.mark.parametrize('mutation',['extra_identity','missing_identity','wrong_hash','wrong_parent','wrong_link_delta','wrong_object','wrong_checks','unknown_evidence','wrong_git','before_after','false_durable','wrong_program'])
def test_semantically_invalid_evidence(mutation):
    events=list(EVENTS);i=next(i for i,e in enumerate(events) if e['operation_id']=='O001' and e['event']=='BEFORE');e=copy.deepcopy(events[i]);events[i]=e
    q='/opt/aios-src/.git/HEAD';reason=''
    if mutation=='extra_identity':e['before_identity'][q]['extra']=1;reason='evidence identity shape'
    elif mutation=='missing_identity':del e['before_identity'][q]['ino'];reason='evidence identity shape'
    elif mutation=='wrong_hash':e['content_sha256']['ORIGINAL:M_HEAD']=digest('bad');reason='content evidence specification'
    elif mutation=='wrong_parent':e['parent_before_identity']={};reason='before parent evidence'
    elif mutation=='wrong_link_delta':e['link_count_changes']={'ORIGINAL:M_HEAD':{'before':2,'after':3}};reason='link change evidence'
    elif mutation=='wrong_object':e['expected_git_oid_if_object']['oid']='0'*40;reason='object evidence specification'
    elif mutation=='wrong_checks':e['durability_checks']['evidence']['checks']=[];reason='evidence checks association'
    elif mutation=='unknown_evidence':e['durability_checks']['evidence']['unknown']=True;reason='evidence proof shape'
    elif mutation=='wrong_git':e['durability_checks']['evidence']['git_facts']={};reason='evidence Git fields'
    elif mutation=='before_after':e['after_identity'][q]['ino']+=1;reason='identity/type/owner/mode/hash mismatch'
    elif mutation=='false_durable':e['durability_checks']['durable']=False;reason='unverified or nondurable event'
    else:e['durability_checks']['program_sha256']='0'*64;reason='wrong program digest'
    stopped(reason,lambda:replay(events))

@pytest.mark.parametrize('mutation',['hash','truncate','reorder','unknown_field','duplicate_key','noncanonical'])
def test_structural_chain_rejection(mutation):
    b,n=encode(EVENTS[:4]);x=json.loads(b[1]);reason=''
    if mutation=='hash':x['previous_event_sha256']='0'*64;b[1]=m.canonical(x);reason='chain/attempt mismatch'
    elif mutation=='truncate':b[1]=b[1][:20];reason='malformed event'
    elif mutation=='reorder':b[1],b[2]=b[2],b[1];reason='ordinal/gap'
    elif mutation=='unknown_field':x['unknown']=True;b[1]=m.canonical(x);reason='closed/canonical event'
    elif mutation=='duplicate_key':b[1]=b'{"ordinal":2,'+b[1][1:];reason='duplicate key'
    else:b[1]+=b'\n';reason='closed/canonical event'
    stopped(reason,lambda:m.validate_chain(b,n,{o['operation_id'] for o in OPS},P['rollback_protocol']['attempt_root'],now_utc=NOW))

@pytest.mark.parametrize('subject',['M_INDEX','M_HEAD'])
@pytest.mark.parametrize('row',ROWS)
def test_all_metadata_rows(row,subject):
    # Independent, explicit row-to-history recipes. No history labels replace replay.
    recipes={
      ('FORWARD','LINK_CANDIDATE'):('intent',None,[]),
      ('FORWARD','FORWARD_EXCHANGE'):('link',None,['retain_candidate']),
      ('FORWARD','RETAIN_FORWARD_OLD'):('exchange',None,['retain_forward','link_original','reverse','retain_candidate']),
      ('FORWARD','VERIFY_FORWARD_COMPLETE'):('move',None,['link_original','reverse','retain_candidate']),
      ('ROLLBACK','RETAIN_FORWARD_OLD'):('exchange',None,['retain_forward','link_original','reverse','retain_candidate']),
      ('ROLLBACK','LINK_ORIGINAL'):('move',None,['link_original','reverse','retain_candidate']),
      ('ROLLBACK','REVERSE_EXCHANGE'):('move','link_original',['link_original','reverse','retain_candidate']),
      ('ROLLBACK','RETAIN_ROLLBACK_NEW'):('move','reverse',['link_original','reverse','retain_candidate']),
      ('ROLLBACK','VERIFY_ROLLBACK_COMPLETE'):('move','retain_candidate',['link_original','reverse','retain_candidate']),
      ('ROLLBACK','CANCEL_UNEXCHANGED_LOCK'):('link',None,['retain_candidate']),
      ('ROLLBACK','VERIFY_UNTOUCHED'):('intent',None,[]),
      ('ROLLBACK','VERIFY_CANCELLED'):('link','retain_candidate',['retain_candidate'])}
    position,after,suffixes=recipes[row['direction'],row['action']]
    cut=next(i+1 for i,e in enumerate(EVENTS) if e['operation_id']==subject and
             (e['event']=='INTENT' if position=='intent' else e['event']=='AFTER' and e['durability_checks']['microstep_id'].endswith('.'+position)))
    own=['ROLLBACK.'+subject+'.'+v for v in suffixes]
    others=[x['id'] for x in P['rollback_occurrences'] if x['subject_operation'] in
            (['M_INDEX','F003','F002','F001','D010'] if subject=='M_HEAD' else ['F003','F002','F001','D010']) and not x['id'].endswith('.retain_forward')]
    plan=own+others
    events,ctx,cuts,entry,target,_=rollback_history(cut,plan)
    if row['direction']=='FORWARD':
        history=replay(EVENTS[:cut]);ns=history.namespace
        assert history.active==subject and history.terminal is None
        expected_index={'intent':0,'link':1,'exchange':2,'move':3}[position]
        assert history.microstep_index==expected_index and history.awaiting_after is False
        assert history.sealed==tuple(m.STATES[:5 if subject=='M_INDEX' else 6])
        nxt=choice(EVENTS[:cut])
        expected_mid={'intent':subject+'.001.link','link':subject+'.002.exchange','exchange':subject+'.003.move','move':'COMPLETE'}[position]
        assert (nxt.action,nxt.operation_id,nxt.microstep_id,nxt.state)==('APPEND_DONE_ONLY' if position=='move' else 'APPEND_BEFORE_ONLY',subject,expected_mid,'INDEX_RECONCILED' if subject=='M_INDEX' else 'HEAD_RECONCILED')
    else:
        phase='RESTORE_HEAD' if subject=='M_HEAD' else 'RESTORE_INDEX'
        if after:
            n=next(i+1 for i,e in enumerate(events) if e['operation_id']=='ROLLBACK' and e['event']=='DONE' and e['durability_checks']['microstep_id']=='ROLLBACK.'+subject+'.'+after)
        elif own:
            n=next(i for i,e in enumerate(events) if e['event']=='BEFORE' and e['durability_checks']['microstep_id']==own[0])
        else:n=cuts[phase]
        history=rb_replay(events[:n],ctx);ns=history['namespace']
        completed_count=0 if after is None else suffixes.index(after)+1
        assert history['completed']==tuple(own[:completed_count])
        assert history['terminal'] is None
        assert (history['next_event'],history['next_microstep'])==(('BEFORE',own[completed_count]) if completed_count<len(own) else ('DONE','BARRIER:'+phase))
    rule=next(o['rule'] for o in OPS if o['operation_id']==subject)
    labels={None:'ABSENT','ORIGINAL:'+subject:'ORIGINAL','CANDIDATE:'+subject:'CANDIDATE'}
    assert [labels[ns[rule[k]]] for k in ('path','lock_path','quarantine_forward_old','quarantine_rollback_new')]==[row[k] for k in ('live','lock','forward_old','rollback_new')]
    assert m.metadata_recovery(*[row[k] for k in ('direction','live','lock','forward_old','rollback_new')])==row['action']
    decision=m.metadata_rollback_decision(P,history,subject)
    remaining=own if row['direction']=='FORWARD' else own[0 if after is None else suffixes.index(after)+1:]
    assert decision['remaining']==tuple(remaining)
    expected_action={'LINK_CANDIDATE':'VERIFY_UNTOUCHED','FORWARD_EXCHANGE':'CANCEL_UNEXCHANGED_LOCK','VERIFY_FORWARD_COMPLETE':'LINK_ORIGINAL'}.get(row['action'],row['action'])
    assert decision['action']==expected_action
    assert decision['target']=={rule['path']:'ORIGINAL:'+subject,rule['lock_path']:None}
    terminal=rb_replay(events,ctx)
    assert terminal['terminal']=='ROLLED_BACK' and terminal['completed']==tuple(plan)
    assert terminal['namespace']==target
    assert all(target[k]==v for k,v in decision['target'].items())
    assert target[rule['quarantine_forward_old']]==('ORIGINAL:'+subject if position in ('exchange','move') else None)
    assert target[rule['quarantine_rollback_new']]==(None if position=='intent' else 'CANDIDATE:'+subject)
    for group in P['baseline_alias_groups']:
        assert all(terminal['namespace'][path]==group['token'] and terminal['observed'][path]['ino']==group['identity']['ino'] and terminal['observed'][path]['nlink']==group['expected_nlink'] for path in group['paths'])
    pre=rb_replay(events[:cuts['PRE_ROLLBACK_SEAL']],ctx)
    assert m.validate_rollback_barrier(P,pre,'PRE_ROLLBACK_SEAL',list(pre['barriers']),plan,entry,pre['observed'],pre['bindings'],git_rollback(pre['namespace'],True),custody_ok=True,entry_proof_ok=True) is True
    assert m.verify_terminal(P,terminal,terminal['observed'],terminal['bindings'],git_rollback(target,True),custody_ok=True) is True

@pytest.mark.parametrize('row',INVALID)
def test_invalid_metadata_combinations(row):
    stopped('metadata ambiguity',lambda:m.metadata_recovery(*row))
    cut=next(i+1 for i,e in enumerate(EVENTS) if e['operation_id']=='M_INDEX' and e['event']=='INTENT')
    h=replay(EVENTS[:cut])
    assert h.active=='M_INDEX' and h.microstep_index==0 and h.namespace['/opt/aios-src/.git/index']=='ORIGINAL:M_INDEX'
    assert choice(EVENTS[:cut]).microstep_id=='M_INDEX.001.link'
    rule=next(o['rule'] for o in OPS if o['operation_id']=='M_INDEX')
    original=copy.deepcopy(h.observed[rule['path']])
    candidate=copy.deepcopy(h.observed[next(o for o in OPS if o['operation_id']=='M_INDEX')['microsteps'][0]['source']])
    foreign={**original,'ino':original['ino']+90000000}
    samples={'ORIGINAL':original,'CANDIDATE':candidate,'ABSENT':None,'FOREIGN':foreign}
    e=copy.deepcopy(EVENTS[cut])
    for key,label in zip(('path','lock_path','quarantine_forward_old','quarantine_rollback_new'),row[1:]):
        e['before_identity'][rule[key]]=copy.deepcopy(samples[label])
    # The first changed path determines an explicit identity/absence rejection;
    # no unrecorded metadata combination may be accepted as a replayed state.
    path=next(q for q in h.namespace if h.observed[q]!=e['before_identity'][q])
    reason='unexpected present path' if h.namespace[path] is None else 'identity shape' if e['before_identity'][path] is None else 'identity/type/owner/mode/hash mismatch'
    stopped(reason,lambda:replay(list(EVENTS[:cut])+[e]))

def rollback_history(cut,plan):
    events=list(EVENTS[:cut]);h=replay(events);ns=dict(h.namespace);b=copy.deepcopy(h.bindings);ctx=copy.deepcopy(CTX);ctx['rollback_plan']=plan
    entry=dict(ns);cuts={}
    def emit(oid,kind,mid,state,step=None):
        nonlocal ns,b
        e,ns,b=event(oid,kind,mid,state,ns,b,ctx,step);events.append(e)
    emit('ROLLBACK','INTENT','ENTER_ROLLBACK','ROLLBACK_INTENT')
    for index,phase in enumerate(PHASES[:-1]):
        if 1<=index<=6:
            subject=['M_HEAD','M_INDEX','F003','F002','F001','D010'][index-1]
            for s in P['rollback_occurrences']:
                if s['id'] in plan and s['subject_operation']==subject:
                    for kind in ('BEFORE','AFTER','DONE'):emit('ROLLBACK',kind,s['id'],'ROLLBACK_INTENT',s)
        cuts[phase]=len(events)
        emit('ROLLBACK','DONE','BARRIER:'+phase,'ROLLBACK_INTENT')
    emit('FINAL','DONE','SEAL:ROLLED_BACK','ROLLED_BACK');cuts['POST_ROLLBACK_TERMINAL']=len(events)
    return events,ctx,cuts,entry,ns,b

def rb_replay(events,ctx):
    b,n=encode(events)
    m.validate_chain(b,n,{o['operation_id'] for o in OPS},P['rollback_protocol']['attempt_root'],now_utc=NOW)
    return m.semantic_rollback_replay(P,b,n,now_utc=NOW,rollback_plan=ctx['rollback_plan'],evidence_context=ctx)

FULL_PLAN=[s['id'] for s in P['rollback_occurrences'] if not s['id'].endswith('.retain_forward')]

@pytest.mark.parametrize('phase',PHASES)
def test_pre_and_post_rollback_barriers(phase):
    events,ctx,cuts,entry,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN)
    h=rb_replay(events[:cuts[phase]],ctx)
    assert h['terminal']==('ROLLED_BACK' if phase=='POST_ROLLBACK_TERMINAL' else None)
    assert h['barriers']==tuple(PHASES[:PHASES.index(phase)])
    assert m.validate_rollback_barrier(P,h,phase,list(h['barriers']),FULL_PLAN,entry,h['observed'],h['bindings'],git_rollback(h['namespace'],phase in PHASES[-2:]),custody_ok=True,entry_proof_ok=True) is True

@pytest.mark.parametrize('count',list(range(63)))
def test_partial_objects_with_real_history_and_rollback(count):
    cut=SEALS['OBJECT_DIRECTORIES_CREATED'] if count==0 else DONE[f'O{count:03d}']
    events,ctx,_,entry,target,_=rollback_history(cut,[]);h=rb_replay(events,ctx)
    assert h['terminal']=='ROLLED_BACK' and h['namespace']==entry==target
    for i in range(1,63):
        o=next(o for o in OPS if o['operation_id']==f'O{i:03d}')
        assert h['namespace'][o['rule']['path']]==('CREATED:'+o['operation_id'] if i<=count else None)
    assert m.verify_terminal(P,h,h['observed'],h['bindings'],git_rollback(target,True),custody_ok=True) is True

@pytest.mark.parametrize('count',list(range(4)))
def test_reachable_ancillary_subsets_with_barriers(count):
    cut=SEALS['DIRECTORIES_CREATED'] if count==0 else DONE[f'F{count:03d}']
    plan=[s['id'] for s in P['rollback_occurrences'] if s['subject_operation']=='D010' or s['subject_operation'] in [f'F{i:03d}' for i in range(1,count+1)]]
    events,ctx,_,_,target,_=rollback_history(cut,plan);h=rb_replay(events,ctx)
    for o in (o for o in OPS if o['kind']=='ancillary'):
        assert target[o['rule']['path']] is None
        assert target[o['rule']['quarantine_path']]==('CREATED:'+o['operation_id'] if int(o['operation_id'][1:])<=count else None)
    assert m.verify_terminal(P,h,h['observed'],h['bindings'],git_rollback(target,True),custody_ok=True) is True

@pytest.mark.parametrize('subset',[(False,False,True),(False,True,False),(False,True,True),(True,False,True)])
def test_unreachable_ancillary_subsets_stop(subset):
    # The ordered program has only four legal published prefixes, not eight arbitrary subsets.
    events=list(EVENTS[:SEALS['DIRECTORIES_CREATED']])
    for index,present in enumerate(subset,1):
        if present:
            oid=f'F{index:03d}';start=next(i for i,e in enumerate(EVENTS) if e['operation_id']==oid)
            events.extend(EVENTS[start:DONE[oid]])
    stopped('unexpected present path',lambda:replay(events))

@pytest.mark.parametrize('terminal',['VERIFIED','ROLLED_BACK'])
def test_contradictory_terminal_evidence(terminal):
    if terminal=='VERIFIED':events=list(EVENTS);run=lambda:replay(events)
    else:
        events,ctx,_,_,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN);run=lambda:rb_replay(events,ctx)
    events[-1]=copy.deepcopy(events[-1]);events[-1]['durability_checks']['evidence']['git_facts']['status_class']='FORGED'
    stopped('Git evidence contradiction',run)

@pytest.mark.parametrize('terminal',['VERIFIED','ROLLED_BACK'])
def test_terminal_observation_loss(terminal):
    h=replay(EVENTS) if terminal=='VERIFIED' else None
    if h:ns,b,obs=h.namespace,h.bindings,copy.deepcopy(h.observed);git=P['phase_barriers']['forward']['VERIFIED']['git_predicate']
    else:
        events,ctx,_,_,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN);h=rb_replay(events,ctx);ns,b,obs=h['namespace'],h['bindings'],copy.deepcopy(h['observed']);git=git_rollback(ns,True)
    obs['/opt/aios-src/.git/HEAD']['ino']+=1
    stopped('identity/type/owner/mode/hash mismatch',lambda:m.verify_terminal(P,h,obs,b,git,custody_ok=True))

def test_durable_stop_is_terminal():
    cut=SEALS['PREPARED'];h=replay(EVENTS[:cut]);e,_,_=event('D001','STOP','STOP','STOP',h.namespace,h.bindings,CTX)
    events=list(EVENTS[:cut])+[e];history=replay(events)
    assert history.halted is True and history.completed==('PREPARE',) and history.sealed==('PREPARED',)
    stopped('custody/invariant/STOP',lambda:choice(events))
    stopped('event after STOP/terminal',lambda:replay(events+[e]))

def test_execution_release_is_not_created():
    stopped('execution withheld',lambda:choice([],execution_release_ok=False))
    assert all(P['execution_release_inputs'][k] is None for k in ('execution_authorization','isolated_test_acceptance','reviewed_syscall_adapter_digest'))

@pytest.mark.parametrize('mutation',['missing_staged','duplicate_staged','reordered_seal','forged_done','unknown_mid','missing_intent'])
def test_semantic_event_order_and_seal_regressions(mutation):
    events=list(EVENTS)
    if mutation in ('missing_staged','duplicate_staged'):
        i=next(i for i,e in enumerate(events) if e['event']=='STAGED')
        if mutation=='missing_staged':del events[i]
        else:events.insert(i,events[i])
        reason='microstep/path mismatch'
    elif mutation=='reordered_seal':
        i=SEALS['PREPARED']-1;e=copy.deepcopy(events[i]);events[i]=e
        e['state']='OBJECT_DIRECTORIES_CREATED';e['durability_checks']['microstep_id']='SEAL:OBJECT_DIRECTORIES_CREATED'
        e['durability_checks']['evidence']['checks']=['STATE_SEAL','SEAL:OBJECT_DIRECTORIES_CREATED','OBJECT_DIRECTORIES_CREATED']
        reason='seal namespace contradiction'
    elif mutation=='forged_done':
        ns,b,ctx=fixture();e,_,_=event('PREPARE','DONE','COMPLETE','PREPARED',ns,b,ctx)
        events=events[:1]+[e];reason='forged/premature DONE'
    elif mutation=='unknown_mid':
        e=copy.deepcopy(events[1]);events[1]=e;e['durability_checks']['microstep_id']='UNKNOWN';e['durability_checks']['evidence']['checks'][1]='UNKNOWN'
        reason='microstep/path mismatch'
    else:del events[0];reason='operation event without INTENT'
    stopped(reason,lambda:replay(events))

@pytest.mark.parametrize('phase',PHASES[:-1])
def test_missing_rollback_barrier_cannot_be_supplied_by_caller(phase):
    events,ctx,cuts,_,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN)
    del events[cuts[phase]]
    stopped('rollback event order',lambda:rb_replay(events,ctx))

@pytest.mark.parametrize('cutstate',['ANCILLARY_FILES_CREATED','INDEX_RECONCILED','HEAD_RECONCILED'])
def test_metadata_rollback_target_and_order(cutstate):
    subjects=['F003','F002','F001','D010']
    if cutstate in ('INDEX_RECONCILED','HEAD_RECONCILED'):subjects.insert(0,'M_INDEX')
    if cutstate=='HEAD_RECONCILED':subjects.insert(0,'M_HEAD')
    plan=[s['id'] for s in P['rollback_occurrences'] if s['subject_operation'] in subjects and not s['id'].endswith('.retain_forward')]
    events,ctx,_,_,target,_=rollback_history(SEALS[cutstate],plan);h=rb_replay(events,ctx)
    assert h['completed']==tuple(plan) and h['namespace']==target and h['terminal']=='ROLLED_BACK'
    assert target['/opt/aios-src/.git/HEAD']=='ORIGINAL:M_HEAD' and target['/opt/aios-src/.git/index']=='ORIGINAL:M_INDEX'
    assert target['/opt/aios-src/.git/HEAD.lock'] is None and target['/opt/aios-src/.git/index.lock'] is None
    assert m.verify_terminal(P,h,h['observed'],h['bindings'],git_rollback(target,True),custody_ok=True) is True

@pytest.mark.parametrize('state',list(m.STATES))
@pytest.mark.parametrize('field',['head','index_identity','status_class','worktree_identity'])
def test_exact_phase_git_predicates(state,field):
    h=replay(EVENTS[:SEALS[state]]);facts=dict(P['phase_barriers']['forward'][state]['git_predicate']);facts[field]='WRONG'
    stopped('HEAD/index/worktree/status phase mismatch',lambda:m.validate_forward_barrier(P,h,state,h.observed,h.bindings,facts,custody_ok=True))

@pytest.mark.parametrize('phase',PHASES)
@pytest.mark.parametrize('fault',['inode','link_count','git','history','custody'])
def test_each_rollback_barrier_rejects_inconsistent_evidence(phase,fault):
    events,ctx,cuts,entry,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN);h=rb_replay(events[:cuts[phase]],ctx)
    obs=copy.deepcopy(h['observed']);git=git_rollback(h['namespace'],phase in PHASES[-2:]);prior=list(h['barriers']);reason=''
    if fault=='inode':obs['/opt/aios-src/.git/HEAD']['ino']+=1;reason='identity/type/owner/mode/hash mismatch'
    elif fault=='link_count':obs['/opt/aios-src/.git/HEAD']['nlink']+=1;reason='link count'
    elif fault=='git':git['head_identity']='FOREIGN';reason='rollback Git/worktree facts'
    elif fault=='history':prior.append('FORGED');reason='rollback barrier history'
    else:reason='rollback phase/custody/entry proof'
    stopped(reason,lambda:m.validate_rollback_barrier(P,h,phase,prior,FULL_PLAN,entry,obs,h['bindings'],git,custody_ok=fault!='custody',entry_proof_ok=True))

def test_head_only_incomplete_cannot_be_accepted():
    h=replay(EVENTS[:SEALS['ANCILLARY_FILES_CREATED']]);ns=dict(h.namespace);b=copy.deepcopy(h.bindings)
    e,_,_=event('M_HEAD','INTENT','BEGIN','HEAD_RECONCILED',ns,b,CTX)
    stopped('missing prior seal/out-of-order operation',lambda:replay(EVENTS[:SEALS['ANCILLARY_FILES_CREATED']]+[e]))

def test_preseal_has_no_terminal_and_postseal_requires_terminal():
    events,ctx,cuts,entry,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN)
    pre=rb_replay(events[:cuts['PRE_ROLLBACK_SEAL']],ctx)
    assert pre['terminal'] is None and pre['next_microstep']=='BARRIER:PRE_ROLLBACK_SEAL'
    assert m.validate_rollback_barrier(P,pre,'PRE_ROLLBACK_SEAL',list(pre['barriers']),FULL_PLAN,entry,pre['observed'],pre['bindings'],git_rollback(pre['namespace'],True),custody_ok=True,entry_proof_ok=True) is True
    stopped('terminal state',lambda:m.verify_terminal(P,pre,pre['observed'],pre['bindings'],git_rollback(pre['namespace'],True),custody_ok=True))

@pytest.mark.parametrize('oid',['D001','D010'])
@pytest.mark.parametrize('position',['staged','published'])
def test_partial_directory_history_and_rollback(oid,position):
    o=next(o for o in OPS if o['operation_id']==oid)
    cut=next(i+1 for i,e in enumerate(EVENTS) if e['operation_id']==oid and
             (e['event']=='STAGED' if position=='staged' else e['event']=='AFTER' and e['durability_checks']['microstep_id'].endswith('.move')))
    plan=['ROLLBACK.D010.quarantine'] if oid=='D010' and position=='published' else []
    events,ctx,_,entry,target,_=rollback_history(cut,plan);h=rb_replay(events,ctx)
    assert h['namespace']==target and h['terminal']=='ROLLED_BACK'
    if position=='staged':assert target[o['rule']['staging_path']]=='CREATED:'+oid and target[o['rule']['path']] is None
    elif oid=='D001':assert target[o['rule']['path']]=='CREATED:D001'
    else:assert target[o['rule']['path']] is None and target[o['rule']['quarantine_path']]=='CREATED:D010'
    assert m.verify_terminal(P,h,h['observed'],h['bindings'],git_rollback(target,True),custody_ok=True) is True

@pytest.mark.parametrize('field',['object_type','raw_bytes','raw_sha256'])
def test_object_evidence_must_match_exact_rule(field):
    events=list(EVENTS);i=next(i for i,e in enumerate(events) if e['operation_id']=='O001');e=copy.deepcopy(events[i]);events[i]=e
    e['expected_git_oid_if_object'][field]='blob' if field=='object_type' else 1 if field=='raw_bytes' else '0'*64
    stopped('object evidence specification',lambda:replay(events))


def evidence_prefix(kind):
    if kind.startswith('RB_'):
        events,ctx,_,_,_,_=rollback_history(SEALS['HEAD_RECONCILED'],FULL_PLAN)
        i=len(events)-1 if kind=='RB_SEAL' else next(i for i,e in enumerate(events) if e['operation_id']=='ROLLBACK' and e['event']==kind[3:] and not e['durability_checks']['microstep_id'].startswith('BARRIER:'))
        return list(events[:i+1]),ctx,True
    if kind=='STOP':
        cut=SEALS['PREPARED'];h=replay(EVENTS[:cut]);e,_,_=event('D001','STOP','STOP','STOP',h.namespace,h.bindings,CTX)
        return list(EVENTS[:cut])+[e],CTX,False
    i=len(EVENTS)-1 if kind=='SEAL' else next(i for i,e in enumerate(EVENTS) if e['operation_id']=='O001' and e['event']==kind)
    return list(EVENTS[:i+1]),CTX,False

@pytest.mark.parametrize('kind',['INTENT','BEFORE','AFTER','STAGED','DONE','SEAL','STOP','RB_BEFORE','RB_DONE','RB_SEAL'])
@pytest.mark.parametrize('bad',[[],{},None,1,True])
@pytest.mark.parametrize('field,reason',[
    ('operation_id','event string type:operation_id'),('event','event string type:event'),
    ('state','event string type:state'),('actual_utc','event string type:actual_utc'),
    ('attempt_root','event string type:attempt_root'),
    ('durability_checks.microstep_id','proof binding type'),
    ('durability_checks.program_sha256','proof binding type'),
    ('durability_checks.evidence.kind','evidence proof types'),
    ('durability_checks.evidence.outcome','evidence outcome type')])
def test_malformed_string_fields_stop_before_semantic_dispatch(kind,bad,field,reason):
    events,ctx,rollback=evidence_prefix(kind);events[-1]=copy.deepcopy(events[-1]);value=events[-1]
    parts=field.split('.')
    for part in parts[:-1]:value=value[part]
    value[parts[-1]]=bad
    blobs,names=encode(events)
    stopped(reason,lambda:m.validate_chain(blobs,names,{o['operation_id'] for o in OPS},P['rollback_protocol']['attempt_root'],now_utc=NOW))
    # pytest.raises(Stop) deliberately does not accept TypeError/KeyError/etc.
    stopped(reason,lambda:m.semantic_rollback_replay(P,blobs,names,now_utc=NOW,rollback_plan=ctx['rollback_plan'],evidence_context=ctx) if rollback else m.semantic_replay(P,blobs,names,now_utc=NOW,evidence_context=ctx))

@pytest.mark.parametrize('mutation,reason',[
    ('stop_list','evidence stop reason type'),('stop_dict','evidence stop reason type'),
    ('stop_null','evidence stop reason type'),('parent_scalar','evidence snapshot shape'),
    ('before_null','evidence snapshot shape'),('after_scalar','evidence snapshot shape'),
    ('identity_type_list','evidence identity type'),('identity_hash_dict','evidence identity hash'),
    ('identity_missing','evidence identity shape'),('identity_unknown','evidence identity shape'),
    ('parent_nested','evidence identity shape'),('content_scalar','evidence content hashes'),
    ('content_hash','evidence content hashes'),('object_type_list','evidence object fields'),
    ('object_hash','evidence object fields'),('object_scalar','evidence object shape'),
    ('links_scalar','evidence link changes shape'),('links_delta','evidence link delta shape'),
    ('links_negative','evidence link delta shape'),('checks_scalar','evidence proof types'),
    ('checks_nested','evidence proof types'),('proof_missing','proof shape'),
    ('proof_unknown','proof shape'),('evidence_missing','evidence proof shape'),
    ('evidence_unknown','evidence proof shape'),('event_missing','closed/canonical event'),
    ('event_unknown','closed/canonical event'),('terminal_scalar','evidence Git shape'),
    ('terminal_nested','evidence Git value type'),('terminal_hash','evidence Git hash'),
    ('terminal_unknown','evidence Git fields'),('rollback_terminal_list','evidence Git list type')])
def test_malformed_nested_evidence_has_exact_stop(mutation,reason):
    kind='STOP' if mutation.startswith('stop_') else 'RB_SEAL' if mutation=='rollback_terminal_list' else 'SEAL' if mutation.startswith('terminal_') else 'BEFORE'
    events,ctx,rollback=evidence_prefix(kind);e=copy.deepcopy(events[-1]);events[-1]=e
    proof=e['durability_checks'];ev=proof['evidence']
    path=next(p for p,i in e['before_identity'].items() if i and i['file_type']=='regular')
    if mutation.startswith('stop_'):ev['stop_reason']={'stop_list':[],'stop_dict':{},'stop_null':None}[mutation]
    elif mutation=='parent_scalar':e['parent_before_identity']=1
    elif mutation=='before_null':e['before_identity']=None
    elif mutation=='after_scalar':e['after_identity']=False
    elif mutation=='identity_type_list':e['before_identity'][path]['file_type']=[]
    elif mutation=='identity_hash_dict':e['before_identity'][path]['sha256']={}
    elif mutation=='identity_missing':del e['before_identity'][path]['ino']
    elif mutation=='identity_unknown':e['before_identity'][path]['unknown']=1
    elif mutation=='parent_nested':e['parent_before_identity'][next(iter(e['parent_before_identity']))]=[]
    elif mutation=='content_scalar':e['content_sha256']=1
    elif mutation=='content_hash':e['content_sha256'][next(iter(e['content_sha256']))]='INVALID'
    elif mutation=='object_type_list':e['expected_git_oid_if_object']['object_type']=[]
    elif mutation=='object_hash':e['expected_git_oid_if_object']['oid']='INVALID'
    elif mutation=='object_scalar':e['expected_git_oid_if_object']=3
    elif mutation=='links_scalar':e['link_count_changes']=1
    elif mutation=='links_delta':e['link_count_changes']={'x':{'before':[],'after':0}}
    elif mutation=='links_negative':e['link_count_changes']={'x':{'before':0,'after':-1}}
    elif mutation=='checks_scalar':ev['checks']=1
    elif mutation=='checks_nested':ev['checks']=[[]]
    elif mutation=='proof_missing':del proof['durable']
    elif mutation=='proof_unknown':proof['unknown']=True
    elif mutation=='evidence_missing':del ev['outcome']
    elif mutation=='evidence_unknown':ev['unknown']=True
    elif mutation=='event_missing':del e['content_sha256']
    elif mutation=='event_unknown':e['unknown']=True
    elif mutation=='terminal_scalar':ev['git_facts']=1
    elif mutation=='terminal_nested':ev['git_facts']['status_class']=[]
    elif mutation=='terminal_hash':ev['git_facts']['head']='INVALID'
    elif mutation=='terminal_unknown':ev['git_facts']['unknown']=True
    else:ev['git_facts']['ancillary_present']=[{}]
    b,n=encode(events)
    schema_reason='evidence stop reason type' if mutation in ('stop_list','stop_dict') else reason
    stopped(schema_reason,lambda:m.validate_chain(b,n,{o['operation_id'] for o in OPS},P['rollback_protocol']['attempt_root'],now_utc=NOW))
    stopped(reason,lambda:m.semantic_rollback_replay(P,b,n,now_utc=NOW,rollback_plan=ctx['rollback_plan'],evidence_context=ctx) if rollback else m.semantic_replay(P,b,n,now_utc=NOW,evidence_context=ctx))

def test_cross_direction_microstep_is_rejected_before_lookup():
    events=list(EVENTS[:2]);events[-1]=copy.deepcopy(events[-1]);e=events[-1]
    e['operation_id']='ROLLBACK';e['state']='ROLLBACK_INTENT'
    e['durability_checks']['evidence']['checks']=['MICROSTEP_BEFORE',e['durability_checks']['microstep_id'],'ROLLBACK_INTENT']
    stopped('microstep/path mismatch',lambda:replay(events))


# M4 v7: PREPARED ONLY. These functions were not imported, collected or executed.
@pytest.fixture(scope='module')
def m4_inventory():
    with (ROOT/'06_FAULT_CASES.json').open(encoding='utf-8') as source_file:
        return json.load(source_file)


def m4_event(data, root):
    packed=data['components'][root]
    return {**packed['scalars'],**{k:None if v is None else data['components'][v]
                                  for k,v in packed['maps'].items()}}


@pytest.fixture(scope='module')
def m4_compiler():
    spec=importlib.util.spec_from_file_location('prepared_inventory_contract',ROOT/'10_fault_inventory.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def m4_files(data,state):
    c=data['components'];packed=c[state['ledger_files']]
    files=[c[h] for b in packed['file_blocks'] for h in c[b]]
    assert len(files)==packed['size'] and [f['path'] for f in files]==sorted({f['path'] for f in files})
    return {f['path']:f for f in files}


M4_SCAN_CACHE={}
M4_EVENT_HASH_CACHE={}


def m4_scan(data,state):
    # Independent oracle reads physical file bytes/hashes and authenticated fixture
    # records. It does not trust supplied ledger_root, proved snapshot or rejection.
    cache_key=(id(data),state['ledger_files'],state.get('external_baseline_witness'))
    if cache_key in M4_SCAN_CACHE:return M4_SCAN_CACHE[cache_key]
    external=state.get('external_baseline_witness')
    bindings=data['components'][data['bound_inputs']]['external_baseline_bindings']
    proved=None
    if external is not None:
        witness=data['components'][external]
        assert external in bindings and bindings[external]==witness
        assert witness['surviving_durable'] is True and witness['approved_scope']=='INITIALIZATION_BASELINE_PROOF_ONLY'
        assert witness['program_sha256']==data['program_sha256'] and witness['attempt_root']==P['rollback_protocol']['attempt_root']
        proved=witness['snapshot']
    terminal=None;prior=None;count=0;reason=None
    for ordinal,(path,f) in enumerate(sorted(m4_files(data,state).items()),1):
        if terminal is not None:reason='FILE_AFTER_TERMINAL';break
        identity=hashlib.sha256(m.canonical({'ledger_inode':path})).hexdigest()
        if (f['file_type'],f['uid'],f['gid'],f['mode'],f['nlink'],f['inode_identity'],f['dev'],f['ino'])!=('regular',1000,1000,0o600,1,identity,2049,10000000000+int(identity[:12],16)):
            reason='UNTRUSTED_FILE_METADATA';break
        record=data['record_catalog'].get((f['content'] or {}).get('sha256'))
        if record is None:reason='PARTIAL_OR_MALFORMED_BYTES';break
        event=m4_event(data,record['payload']);key=(id(data),record['payload'])
        if key not in M4_EVENT_HASH_CACHE:M4_EVENT_HASH_CACHE[key]=hashlib.sha256(m.canonical(event)).hexdigest()
        sha=M4_EVENT_HASH_CACHE[key]
        assert sha==f['content']['sha256']
        if Path(path).name!=f"{ordinal:06d}-{event['operation_id']}-{event['event']}.json" or event['ordinal']!=ordinal or event['previous_event_sha256']!=prior:
            reason='FILENAME_OR_CHAIN_MISMATCH';break
        if count==0 and proved is None:proved=record['before_snapshot']
        if record['before_snapshot']!=proved:reason='PROOF_CONTINUITY_MISMATCH';break
        proved=record['before_snapshot'] if event['event']=='STOP' else record['after_snapshot'];prior=sha;count+=1
        if event['event']=='STOP':terminal='STOP'
        elif event['operation_id']=='FINAL' and event['state'] in ('VERIFIED','ROLLED_BACK'):terminal=event['state']
    M4_SCAN_CACHE[cache_key]=(proved,terminal,count,reason)
    return M4_SCAN_CACHE[cache_key]


def m4_expected_recovery(data,state,fault):
    proved,terminal,count,reason=m4_scan(data,state)
    assert (proved,terminal,count,reason)==(state['last_proved_snapshot'],state['terminal'],state['durable_proof_state']['accepted_record_count'],state['durable_proof_state']['rejection'])
    if reason:return 'STOP_TORN_RECORD' if reason=='PARTIAL_OR_MALFORMED_BYTES' else 'STOP_RECOVERY_REQUIRED'
    success=fault in ('SHORT_WRITE_THEN_SUCCESS','SHORT_READ_THEN_SUCCESS','EINTR_THEN_SUCCESS')
    if success and not any(state['persistent_controls'].values()) and terminal is None:return 'CONTINUE_SAME_CALL'
    different=state['actual_snapshot']!=proved
    if terminal=='STOP' or any(state['persistent_controls'].values()):return 'STOP_AMBIGUOUS_EFFECT' if different else 'STOP_PRESERVE'
    if proved is None or terminal and different:return 'STOP_RECOVERY_REQUIRED'
    if different:return 'STOP_AMBIGUOUS_EFFECT'
    if not success and not fault.startswith(('PROCESS_CRASH','POWER_LOSS')):return 'STOP_PRESERVE'
    if terminal:return 'TERMINAL_INSPECTION_ONLY'
    return 'CONTINUE_PROVED_PREFIX'


@pytest.fixture(scope='module')
def m4_indexes(m4_inventory):
    d=m4_inventory
    return ({c['id']:c for c in d['cases']},{o['id']:o for o in d['origins']},
            {f['id']:f for f in d['fixtures']})


def test_m4_all_stop_payloads_have_normative_closed_schema(m4_inventory):
    found=0
    for node in m4_inventory['components'].values():
        if not isinstance(node,dict) or 'event_sha256' not in node or 'previous' not in node:continue
        e=m4_event(m4_inventory,node['payload'])
        if e['event']!='STOP':continue
        m.validate_event_types(e)
        assert e['after_identity'] is None and e['parent_after_identity'] is None
        assert e['link_count_changes'] is None and e['source_path'] is None and e['destination_path'] is None
        assert e['durability_checks']['evidence']=={'kind':'STOP','git_facts':None,'checks':[],
                                                   'stop_reason':'REVOKED','outcome':'UNKNOWN_RETAIN'}
        assert node['after_snapshot'] is None
        if node['previous']:
            previous=m4_inventory['components'][node['previous']]
            assert node['before_snapshot']==previous['after_snapshot']
        found+=1
    assert found>0


def test_m4_stop_after_mutation_uses_last_proved_snapshot(m4_inventory):
    d=m4_inventory;found=0
    for f in d['fixtures']:
        frame=f['initial_frame']
        if f['direction']!='STOP_LEDGER' or frame['actual_snapshot']==frame['last_proved_snapshot']:continue
        e=m4_event(d,f['record']['payload'])
        if frame['last_proved_snapshot'] is None:
            # Initial record construction has verified live observations, but
            # no surviving record yet proves them across a crash.
            assert frame['ledger_root'] is None and frame['durable_proof_state']['source']=='NONE'
            assert frame['durable_proof_state']['base_snapshot'] is None
            assert f['record']['before_snapshot']==frame['actual_snapshot']
            continue
        assert f['record']['before_snapshot']==frame['last_proved_snapshot']
        previous=d['components'][frame['ledger_root']]
        prior=m4_event(d,previous['payload'])
        assert e['before_identity']==prior['after_identity']
        assert e['content_sha256']==prior['content_sha256']
        found+=1
    assert found>=len(P['rollback_occurrences'])


@pytest.mark.parametrize('terminal',['TORN','STOP'])
def test_m4_torn_and_durable_stop_always_halt(terminal,m4_inventory):
    found=0
    for state in m4_inventory['states'].values():
        matches=state['durable_proof_state']['rejection']=='PARTIAL_OR_MALFORMED_BYTES' if terminal=='TORN' else state['terminal']=='STOP'
        if matches:
            assert state['required_recovery_action'].startswith('STOP_');found+=1
    assert found


@pytest.mark.parametrize('stream',['FORWARD','ROLLBACK'])
def test_m4_no_unauthorized_resumption(stream,m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for origin in origins.values():
        f=fixtures[origin['fixture_id']]
        if f['direction']!='STOP_LEDGER':continue
        rollback=f['normative_cursor'][0]=='ROLLBACK'
        if rollback!=(stream=='ROLLBACK'):continue
        state=m4_inventory['states'][cases[origin['case_id']]['semantic_state_fingerprint']]
        assert state['persistent_controls']['release_revoked'] is True
        assert state['required_recovery_action'].startswith('STOP_');found+=1
    assert found


def test_m4_process_and_power_loss_same_survivor_collapse(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;count=0
    for f in fixtures.values():
        for i,call in enumerate(f['calls'],1):
            if not call['action'].startswith('fsync'):continue
            for a,b in [('PROCESS_CRASH_BEFORE','POWER_LOSS_BEFORE_DURABILITY'),
                        ('PROCESS_CRASH_AFTER','POWER_LOSS_AFTER_DURABILITY')]:
                x=origins[f"{f['id']}:call{i:03d}:{a}:exact-survivor"]
                y=origins[f"{f['id']}:call{i:03d}:{b}:exact-survivor"]
                assert x['case_id']==y['case_id'];count+=1
    assert count


def test_m4_no_annotation_only_ambiguity_split(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        if f['direction']!='LEDGER':continue
        i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='fchmod_new_fd')
        x=origins[f"{f['id']}:call{i:03d}:EIO:unchanged"]
        y=origins[f"{f['id']}:call{i+1:03d}:EIO:unchanged"]
        assert x['case_id']==y['case_id'];found+=1
    assert found
    assert all('disturbance' not in s for s in m4_inventory['states'].values())


def test_m4_distinct_retained_prefixes_do_not_collapse(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        for i,call in enumerate(f['calls'],1):
            if call['action']!='write_all':continue
            if f['record'] is None:
                excluded={x['origin_fault_site_id'] for x in m4_inventory['candidate_exclusions']}
                for n in (1,2):assert f"{f['id']}:call{i:03d}:CRASH_DURING_PARTIAL_WRITE:prefix-{n}" in excluded
                continue
            a=origins[f"{f['id']}:call{i:03d}:CRASH_DURING_PARTIAL_WRITE:prefix-1"]
            b=origins[f"{f['id']}:call{i:03d}:CRASH_DURING_PARTIAL_WRITE:prefix-2"]
            empty=origins[f"{f['id']}:call{i:03d}:PROCESS_CRASH_BEFORE:exact-survivor"]
            assert len({a['case_id'],b['case_id'],empty['case_id']})==3
            if f['record']:
                full=m.canonical(m4_event(m4_inventory,f['record']['payload']))
                for length,origin in [(1,a),(2,b)]:
                    state=m4_inventory['states'][cases[origin['case_id']]['semantic_state_fingerprint']]
                    assert m4_files(m4_inventory,state)[call['path']]['content']['sha256']==hashlib.sha256(full[:length]).hexdigest()
            found+=1
    assert found


def test_m4_distinct_namespace_mutations_remain_distinct(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        for i,call in enumerate(f['calls'],1):
            if call['action'] not in ('linkat_flags0','renameat2_NOREPLACE','renameat2_EXCHANGE','mkdirat'):continue
            a=origins[f"{f['id']}:call{i:03d}:PROCESS_CRASH_BEFORE:exact-survivor"]
            b=origins[f"{f['id']}:call{i:03d}:PROCESS_CRASH_AFTER:exact-survivor"]
            sa=m4_inventory['states'][cases[a['case_id']]['semantic_state_fingerprint']]
            sb=m4_inventory['states'][cases[b['case_id']]['semantic_state_fingerprint']]
            assert sa['actual_snapshot']!=sb['actual_snapshot'] and a['case_id']!=b['case_id'];found+=1
    assert found


def test_m4_canonical_fingerprints_and_complete_origins(m4_inventory,m4_indexes):
    cases,origins,_=m4_indexes;covered=[]
    for key,state in m4_inventory['states'].items():
        assert hashlib.sha256(m.canonical(state)).hexdigest()==key
        assert hashlib.sha256(m.canonical(dict(reversed(list(state.items()))))).hexdigest()==key
        assert 'C'+key in cases
    for case in cases.values():
        for origin in case['origin_fault_site_ids']:
            assert origins[origin]['case_id']==case['id'];covered.append(origin)
    assert len(covered)==len(set(covered))==len(origins)


def test_m4_every_surviving_oracle_recomputed_independently(m4_inventory,m4_indexes):
    cases,origins,_=m4_indexes
    for origin in origins.values():
        case=cases[origin['case_id']];state=m4_inventory['states'][case['semantic_state_fingerprint']]
        assert state['required_recovery_action']==m4_expected_recovery(m4_inventory,state,origin['failure_mode'])
        assert case['required_recovery_action']==state['required_recovery_action']


@pytest.mark.parametrize('step',P['rollback_occurrences'])
def test_m4_rollback_before_and_write_fault_boundaries(step,m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        if f['direction']!='ROLLBACK' or f['step']!=step['id']:continue
        frame=f['initial_frame'];node=m4_inventory['components'][frame['ledger_root']]
        event=m4_event(m4_inventory,node['payload'])
        assert event['event']=='BEFORE' and event['durability_checks']['microstep_id']==step['id']
        before_write=next(x for x in fixtures.values() if x['direction']=='LEDGER'
                          and x['record']['payload']==node['payload'])
        assert before_write['initial_frame']['ledger_root']==node['previous']
        i=next(i for i,c in enumerate(before_write['calls'],1) if c['action']=='write_all')
        o=origins[f"{before_write['id']}:call{i:03d}:CRASH_DURING_PARTIAL_WRITE:prefix-1"]
        state=m4_inventory['states'][cases[o['case_id']]['semantic_state_fingerprint']]
        assert state['ledger_root']==node['previous'] and state['required_recovery_action']=='STOP_TORN_RECORD'
        found+=1
    assert found


def test_m4_all_surviving_ledger_outcomes_use_normative_semantic_replay(m4_inventory):
    d=m4_inventory;components=d['components'];inputs=components[d['bound_inputs']]
    roots={s['ledger_root'] for s in d['states'].values()}-{None}
    for root in roots:
        nodes=[];current=root
        while current is not None:
            node=components[current];nodes.append(node);current=node['previous']
        nodes.reverse();events=[m4_event(d,n['payload']) for n in nodes]
        first=components[nodes[0]['before_snapshot']]
        ns=components[first['namespace']];inodes=components[first['inodes']]
        ctx={'initial_bindings':{},'content_hashes':{t:c['sha256'] for t,c in inputs['full_content'].items()},'rollback_plan':[]}
        for token,i in inodes.items():
            ctx['initial_bindings'][token]={'identity':{**{k:i[k] for k in ('dev','ino','uid','gid','mode','file_type')},
                                                       'sha256':None if i['file_type']=='directory' else i['content']['sha256']},
                                             'outside_links':i['outside_links']}
        rollback=next((n['rollback_plan'] for n in nodes if n['rollback_plan'] is not None),None)
        blobs=[m.canonical(e) for e in events]
        names=[f"{e['ordinal']:06d}-{e['operation_id']}-{e['event']}.json" for e in events]
        m.validate_chain(blobs,names,{o['operation_id'] for o in OPS},P['rollback_protocol']['attempt_root'],now_utc=NOW)
        if rollback is None:
            h=m.semantic_replay(P,blobs,names,now_utc=NOW,evidence_context=ctx)
            assert h.halted==(events[-1]['event']=='STOP')
        else:
            ctx['rollback_plan']=rollback
            run=lambda:m.semantic_rollback_replay(P,blobs,names,now_utc=NOW,rollback_plan=rollback,evidence_context=ctx)
            if events[-1]['event']=='STOP':stopped('rollback STOP',run)
            else:run()


def test_m4_exclusions_and_fresh_accounting(m4_inventory,m4_indexes):
    d=m4_inventory;cases,origins,_=m4_indexes
    assert all(x['classification'] in ('INVALID_COMPILER_CASE','INVALID_FILESYSTEM_REALIZABILITY','UNBOUND_COVERAGE_OBLIGATION') and x['reason'] for x in d['candidate_exclusions'])
    assert d['raw_applicable_combinations']==len(origins)+len(d['candidate_exclusions'])
    assert d['raw_generated_combinations']-d['inapplicable_combinations_excluded']-d['invalid_compiler_cases_excluded']-d['invalid_filesystem_realizability_excluded']-d['unbound_coverage_obligations']-d['semantic_equivalents_removed']==len(cases)
    assert d['independent_validation']['generated_outcomes_checked']==len(origins)


def test_m4_different_retained_corruption_bytes_remain_distinct(m4_inventory):
    d=m4_inventory;grouped={};found=0
    for key,encoded in d['byte_blobs'].items():
        assert hashlib.sha256(bytes.fromhex(encoded)).hexdigest()==key
    for fingerprint,state in d['states'].items():
        snap=d['components'][state['actual_snapshot']]
        inodes=d['components'][snap['inodes']]
        for token,inode in inodes.items():
            content=inode['content']
            if not content or 'sha256' not in content or content['sha256'] not in d['byte_blobs']:continue
            h=content['sha256'];prior=grouped.get(token)
            if prior and prior[0]!=h:
                assert prior[1]!=fingerprint
                assert d['byte_blobs'][prior[0]]!=d['byte_blobs'][h];found+=1
            grouped[token]=(h,fingerprint)
    assert found


def test_m4_parent_fsync_identical_survivors_collapse(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        if f['direction'] not in ('LEDGER','STOP_LEDGER'):continue
        i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='fsync_parent')
        for before,after in [('PROCESS_CRASH_BEFORE','PROCESS_CRASH_AFTER'),('POWER_LOSS_BEFORE_DURABILITY','POWER_LOSS_AFTER_DURABILITY')]:
            a=origins[f"{f['id']}:call{i:03d}:{before}:exact-survivor"]
            b=origins[f"{f['id']}:call{i:03d}:{after}:exact-survivor"]
            assert a['case_id']==b['case_id'];found+=1
    assert found


def test_m4_complete_bytes_define_proof_without_bookkeeping(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        if f['record'] is None:continue
        i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='write_all')
        o=origins[f"{f['id']}:call{i:03d}:PROCESS_CRASH_AFTER:exact-survivor"]
        s=m4_inventory['states'][cases[o['case_id']]['semantic_state_fingerprint']]
        proved,terminal,count,reason=m4_scan(m4_inventory,s)
        assert reason is None and count>0
        assert proved==(f['record']['before_snapshot'] if f['direction']=='STOP_LEDGER' else f['record']['after_snapshot'])
        assert 'pending_ledger_file' not in s and 'fsync_completed' not in s
        assert s['last_proved_snapshot']==proved;found+=1
    assert found


@pytest.mark.parametrize('fault',['WRONG_MODE','WRONG_OWNER','WRONG_GROUP'])
def test_m4_valid_ledger_metadata_faults_retained(fault,m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        if f['record'] is None:continue
        created=False
        for i,c in enumerate(f['calls'],1):
            if c['action']=='openat_O_EXCL_NOFOLLOW':created=True;continue
            if not created or c['action']!='fstat_verify_regular':continue
            o=origins[f"{f['id']}:call{i:03d}:{fault}:assigned"]
            s=m4_inventory['states'][cases[o['case_id']]['semantic_state_fingerprint']]
            file=m4_files(m4_inventory,s)[c['path']]
            field,value={'WRONG_MODE':('mode',0o777),'WRONG_OWNER':('uid',1001),'WRONG_GROUP':('gid',1001)}[fault]
            assert file[field]==value and s['required_recovery_action'].startswith('STOP_');found+=1
    assert found


def test_m4_impossible_root_replacement_is_excluded(m4_inventory,m4_indexes):
    _,origins,fixtures=m4_indexes
    excluded={e['origin_fault_site_id']:e for e in m4_inventory['candidate_exclusions']};found=0
    for f in fixtures.values():
        for i,c in enumerate(f['calls'],1):
            if c['path']!='/' or c['action']!='openat_DIRECTORY_NOFOLLOW':continue
            key=f"{f['id']}:call{i:03d}:SYMLINK_COMPONENT:assigned"
            assert key not in origins and excluded[key]['classification']=='INVALID_FILESYSTEM_REALIZABILITY';found+=1
    assert found
    held=0
    for f in fixtures.values():
        for i,c in enumerate(f['calls'],1):
            if not c['action'].startswith('fstat_') or c['role']=='object':continue
            key=f"{f['id']}:call{i:03d}:WRONG_TYPE:assigned"
            assert key not in origins and excluded[key]['classification']=='INVALID_FILESYSTEM_REALIZABILITY';held+=1
    assert held


@pytest.mark.parametrize('fault',['root','root_dot','parent','directory_link','directory_nlink','nonempty_remove','cross_device','mount_remove','bind_mount_move','file_directory_replace','absent_exchange'])
def test_m4_impossible_namespace_operations_rejected(fault,m4_compiler):
    root={'dev':1,'ino':1,'uid':1000,'gid':1000,'mode':0o700,'file_type':'directory','outside_links':2,'content':None}
    regular={**root,'ino':3,'file_type':'regular','outside_links':0,'content':{'sha256':hashlib.sha256(b'x').hexdigest()}}
    ns={'/':'r','/d':'d','/d/f':'f'};ins={'r':root,'d':{**root,'ino':2},'f':regular}
    mounts=()
    if fault=='root':ops=[{'syscall':'rmdir','path':'/'}]
    elif fault=='root_dot':ops=[{'syscall':'symlinkat','path':'/.','token':'foreign','inode':{**regular,'file_type':'symlink','mode':0o777,'content':{'target':'/foreign'}}}]
    elif fault=='parent':ops=[{'syscall':'linkat','source':'/d/f','path':'/missing/f'}]
    elif fault=='directory_link':ops=[{'syscall':'linkat','source':'/d','path':'/alias'}]
    elif fault=='directory_nlink':
        ins['d']['outside_links']=3;ops=[]
    elif fault=='mount_remove':
        ns['/mount']='mount';ins['mount']={**root,'ino':4,'dev':2};ops=[{'syscall':'rmdir','path':'/mount'}]
    elif fault=='bind_mount_move':
        mounts=('/d',);ops=[{'syscall':'renameat2_NOREPLACE','source':'/d','path':'/moved'}]
    elif fault=='file_directory_replace':ops=[{'syscall':'renameat2_REPLACE','source':'/d/f','path':'/d'}]
    elif fault=='nonempty_remove':ops=[{'syscall':'rmdir','path':'/d'}]
    elif fault=='cross_device':
        ns['/other']='o';ins['o']={**root,'ino':4,'dev':2};ops=[{'syscall':'renameat2_NOREPLACE','source':'/d/f','path':'/other/f'}]
    else:ops=[{'syscall':'renameat2_EXCHANGE','source':'/d/f','path':'/missing'}]
    with pytest.raises(m4_compiler.InvalidFilesystem):m4_compiler.replay_fault_operations(ns,ins,ops,mount_points=mounts)


def test_m4_valid_ledger_symlink_replacement_has_syscalls(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        if f['record'] is None:continue
        i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='reopenat_NOFOLLOW')
        o=origins[f"{f['id']}:call{i:03d}:SYMLINK_COMPONENT:assigned"]
        operations=m4_inventory['components'][o['fault_operations']]
        assert [x['syscall'] for x in operations]==['symlinkat','renameat2_REPLACE']
        s=m4_inventory['states'][cases[o['case_id']]['semantic_state_fingerprint']]
        assert m4_files(m4_inventory,s)[f['calls'][i-1]['path']]['file_type']=='symlink'
        assert s['required_recovery_action'].startswith('STOP_');found+=1
    assert found


def test_m4_no_blanket_ledger_path_exclusion(m4_inventory,m4_indexes):
    _,origins,fixtures=m4_indexes
    assert not any('foreign ledger-file witness' in x['reason'] for x in m4_inventory['candidate_exclusions'])
    found=0
    for f in fixtures.values():
        if f['record'] is None:continue
        i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='read_and_hash_verify')
        assert f"{f['id']}:call{i:03d}:CONTENT_HASH_MISMATCH:assigned" in origins;found+=1
    assert found


def test_m4_same_inode_rename_preserves_both_aliases(m4_compiler):
    directory={'dev':1,'ino':1,'uid':1000,'gid':1000,'mode':0o700,'file_type':'directory','outside_links':2,'content':None}
    regular={**directory,'ino':2,'file_type':'regular','outside_links':0,'content':{'sha256':hashlib.sha256(b'x').hexdigest()}}
    ns={'/':'root','/a':'file','/b':'file'};ins={'root':directory,'file':regular}
    after,bindings=m4_compiler.replay_fault_operations(ns,ins,[{'syscall':'renameat2_REPLACE','source':'/a','path':'/b'}])
    assert after==ns and bindings==ins


def test_m4_realizable_ledger_ancestor_loss_retains_valid_before_origin(m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    root=P['rollback_protocol']['attempt_root']
    for f in fixtures.values():
        if f['direction'] not in ('FORWARD','ROLLBACK'):continue
        for i,c in enumerate(f['calls'],1):
            if c['path']!=root or c['action']!='openat_DIRECTORY_NOFOLLOW':continue
            o=origins[f"{f['id']}:call{i:03d}:CONCURRENT_NAMESPACE_REPLACEMENT:assigned"]
            s=m4_inventory['states'][cases[o['case_id']]['semantic_state_fingerprint']]
            before=m4_event(m4_inventory,m4_inventory['components'][f['initial_frame']['ledger_root']]['payload'])
            assert before['event']=='BEFORE' and before['durability_checks']['microstep_id']==f['step']
            assert m4_files(m4_inventory,s)=={} and s['ledger_root'] is None
            assert s['actual_snapshot']!=s['last_proved_snapshot']
            assert s['last_proved_snapshot'] is None and s['durable_proof_state']['source']=='NONE'
            assert s['required_recovery_action']=='STOP_RECOVERY_REQUIRED';found+=1
    assert found


def test_m4_pending_to_committed_bookkeeping_cannot_split_state(m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;cases,origins,fixtures=m4_indexes
    f=next(f for f in fixtures.values() if f['direction']=='LEDGER' and
           f['record']['after_snapshot']!=f['record']['before_snapshot'])
    i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='fsync_parent')
    o=origins[f"{f['id']}:call{i:03d}:PROCESS_CRASH_AFTER:exact-survivor"]
    state=d['states'][cases[o['case_id']]['semantic_state_fingerprint']]
    compiler=m4_compiler.Compiler(P);compiler.components=dict(d['components'])
    compiler.records=d['record_catalog']
    committed={k:copy.deepcopy(state[k]) for k in ('ledger_root','last_proved_snapshot','actual_snapshot','persistent_controls','terminal')}
    committed['pending_ledger_file']=None
    pending=copy.deepcopy(committed);node=d['components'][state['ledger_root']]
    pending.update(ledger_root=node['previous'],last_proved_snapshot=node['before_snapshot'],
                   pending_ledger_file=copy.deepcopy(node['file']))
    a=compiler.finish_state(committed,'RESTART');b=compiler.finish_state(pending,'RESTART')
    assert a==b==state and m4_compiler.digest(a)==m4_compiler.digest(b)


@pytest.mark.parametrize('variant',['unchanged','prefix-1'])
def test_m4_acceptance_rejects_unwitnessed_namespace_transition(variant,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;cases,origins,fixtures=m4_indexes
    f=next(f for f in fixtures.values() if f['direction']=='LEDGER')
    i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='write_all')
    fault='PROCESS_CRASH_BEFORE' if variant=='unchanged' else 'PARTIAL_WRITE_THEN_EIO'
    key=f"{f['id']}:call{i:03d}:PARTIAL_WRITE_THEN_EIO:prefix-1"
    state=copy.deepcopy(d['states'][cases[origins[key]['case_id']]['semantic_state_fingerprint']])
    state['actual_snapshot']='invented-namespace-transition'
    checker=m4_compiler.OutcomeAudit(P,d['components'],d['bound_inputs']);checker.catalog=d['record_catalog']
    with pytest.raises(m4_compiler.InvalidFilesystem):
        checker.validate_origin(state,f,i,fault,variant,[],checker.normal_call_snapshots(f),d['byte_blobs'])


@pytest.mark.parametrize('fault',['SYMLINK_COMPONENT','CONCURRENT_NAMESPACE_REPLACEMENT'])
def test_m4_root_child_replacements_are_realizable(fault,m4_inventory,m4_indexes):
    cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        for i,c in enumerate(f['calls'],1):
            q=c['path']
            if not q or not q.startswith('/') or q=='/' or str(Path(q).parent)!='/' or c['action']!='openat_DIRECTORY_NOFOLLOW':continue
            o=origins[f"{f['id']}:call{i:03d}:{fault}:assigned"]
            operations=m4_inventory['components'][o['fault_operations']]
            assert operations[0]['syscall']=='renameat2_NOREPLACE' and operations[0]['source']==q
            assert all(not x['path'].startswith('//') and not x.get('source','').startswith('//') for x in operations)
            state=m4_inventory['states'][cases[o['case_id']]['semantic_state_fingerprint']]
            assert state['required_recovery_action'].startswith('STOP_');found+=1
    assert found


def test_m4_missing_witnesses_are_not_filesystem_impossibilities(m4_inventory,m4_indexes):
    _,_,fixtures=m4_indexes
    rejected={r['origin_fault_site_id']:r for r in m4_inventory['candidate_exclusions']}
    assert not any('unsupported filesystem fault predicate' in r['reason'] or
                   'noncanonical syscall path' in r['reason'] for r in rejected.values())
    found=0
    for f in fixtures.values():
        for i,c in enumerate(f['calls'],1):
            if c['action']!='verify_all_5426_object_identities':continue
            for fault in ('WRONG_LENGTH','WRONG_SHA1','WRONG_SHA256','TRAILING_ZLIB_BYTES'):
                r=rejected[f"{f['id']}:call{i:03d}:{fault}:assigned"]
                assert r['classification']=='UNBOUND_COVERAGE_OBLIGATION' and 'byte witness' in r['reason'];found+=1
    assert found


# M4 v7 additions: prepared only; no test import, collection or execution.
@pytest.mark.parametrize('pair',[
    ('F00002:call027:PROCESS_CRASH_AFTER:exact-survivor','F00003:call001:PROCESS_CRASH_BEFORE:exact-survivor'),
    ('F00002:call014:LINK_COUNT_MISMATCH:assigned','F00003:call012:LINK_COUNT_MISMATCH:assigned'),
    ('F00002:call021:WRONG_OWNER:assigned','F00003:call004:WRONG_OWNER:assigned'),
])
def test_m4_reported_initialization_pairs_collapse(pair,m4_inventory,m4_indexes):
    cases,origins,_=m4_indexes
    a,b=(origins[x] for x in pair)
    assert a['case_id']==b['case_id']
    s=m4_inventory['states'][cases[a['case_id']]['semantic_state_fingerprint']]
    assert s['ledger_root'] is None and s['last_proved_snapshot'] is None
    assert s['durable_proof_state']['source']=='NONE'
    assert s['required_recovery_action']=='STOP_RECOVERY_REQUIRED'


def test_m4_all_physical_groups_have_one_durable_proof(m4_inventory):
    proofs={};fingerprints={}
    for key,s in m4_inventory['states'].items():
        physical=(s['actual_snapshot'],s['ledger_files'],s['external_baseline_witness'],m.canonical(s['persistent_controls']))
        proof=m.canonical({k:s[k] for k in ('ledger_root','last_proved_snapshot','durable_proof_state','terminal')})
        assert proofs.setdefault(physical,proof)==proof
        semantic=physical+(s['uncertainty_class'],s['required_recovery_action'])
        assert fingerprints.setdefault(semantic,key)==key


@pytest.mark.parametrize('bookkeeping',['none','planned_snapshot'])
def test_m4_defaults_cannot_fabricate_initialization_proof(bookkeeping,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;_,_,fixtures=m4_indexes;initial=fixtures['F00003']['initial_frame']
    compiler=m4_compiler.Compiler(P);compiler.components=dict(d['components']);compiler.records=d['record_catalog']
    frame={'ledger_root':None,'pending_ledger_file':None,'last_proved_snapshot':None,
           'actual_snapshot':initial['actual_snapshot'],'terminal':None,'persistent_controls':{'release_revoked':False}}
    if bookkeeping=='planned_snapshot':frame['last_proved_snapshot']=initial['actual_snapshot']
    s=compiler.finish_state(frame,'RESTART')
    assert s['last_proved_snapshot'] is None and s['durable_proof_state']=={
        'base_snapshot':None,'source':'NONE','accepted_record_count':0,'rejection':None}
    assert s['required_recovery_action']=='STOP_RECOVERY_REQUIRED'


@pytest.mark.parametrize('binding',['valid','unbound','nondurable','wrongscope','wrongprogram','missing_evidence','mismatched_approval'])
def test_m4_external_baseline_requires_survival_and_governed_binding(binding,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;_,_,fixtures=m4_indexes;initial=fixtures['F00003']['initial_frame']
    c=m4_compiler.Compiler(P);c.components=dict(d['components']);c.records=d['record_catalog']
    frame={'ledger_root':None,'pending_ledger_file':None,'last_proved_snapshot':None,
           'actual_snapshot':initial['actual_snapshot'],'terminal':None,'persistent_controls':{'release_revoked':False}}
    unproved=c.finish_state(frame,'RESTART')
    evidence={'format':'aios-external-baseline-evidence-v1','snapshot':initial['actual_snapshot'],
              'program_sha256':c.program_hash,'attempt_root':c.root}
    eh=c.intern(evidence)
    approval={'format':'aios-external-baseline-approval-v1','evidence_sha256':eh,
              'program_sha256':c.program_hash,'attempt_root':c.root,'approved_scope':'INITIALIZATION_BASELINE_PROOF_ONLY'}
    if binding=='mismatched_approval':approval['evidence_sha256']='0'*64
    gh=c.intern(approval)
    w={'format':'aios-governed-external-baseline-v1','snapshot':initial['actual_snapshot'],
       'program_sha256':c.program_hash,'attempt_root':c.root,'evidence_sha256':eh,'governance_sha256':gh,
       'surviving_durable':True,'approved_scope':'INITIALIZATION_BASELINE_PROOF_ONLY'}
    if binding=='nondurable':w['surviving_durable']=False
    if binding=='wrongscope':w['approved_scope']='UNAPPROVED'
    if binding=='wrongprogram':w['program_sha256']='0'*64
    ref=c.intern(w);frame['external_baseline_witness']=ref
    if binding!='unbound':c.external_baseline_bindings[ref]=w
    if binding=='missing_evidence':del c.components[eh]
    if binding!='valid':
        with pytest.raises((AssertionError,KeyError)):c.finish_state(frame,'RESTART')
        return
    proved=c.finish_state(frame,'RESTART')
    assert proved['durable_proof_state']['source']=='EXTERNAL_BASELINE'
    assert proved['last_proved_snapshot']==initial['actual_snapshot']
    assert proved['ledger_root'] is None and proved['durable_proof_state']['accepted_record_count']==0
    assert proved['actual_snapshot']==unproved['actual_snapshot'] and proved['ledger_files']==unproved['ledger_files']
    assert m4_compiler.digest(proved)!=m4_compiler.digest(unproved)
    assert proved['required_recovery_action']=='CONTINUE_PROVED_PREFIX'
    bound=c.intern({**d['components'][d['bound_inputs']],'external_baseline_bindings':dict(c.external_baseline_bindings)})
    checker=m4_compiler.OutcomeAudit(P,c.components,bound);checker.catalog=d['record_catalog']
    checker.validate_outcome(proved)


@pytest.mark.parametrize('forgery',['base','source','external_reference','recovery'])
def test_m4_independent_validator_rejects_fabricated_proof(forgery,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;cases,origins,fixtures=m4_indexes
    o=origins['F00003:call001:PROCESS_CRASH_BEFORE:exact-survivor']
    s=copy.deepcopy(d['states'][cases[o['case_id']]['semantic_state_fingerprint']])
    if forgery=='base':s['durable_proof_state']['base_snapshot']=s['actual_snapshot'];s['last_proved_snapshot']=s['actual_snapshot']
    elif forgery=='source':s['durable_proof_state']['source']='LEDGER'
    elif forgery=='external_reference':s['external_baseline_witness']='0'*64
    else:s['required_recovery_action']='CONTINUE_PROVED_PREFIX';s['uncertainty_class']='NONE'
    checker=m4_compiler.OutcomeAudit(P,d['components'],d['bound_inputs']);checker.catalog=d['record_catalog']
    f=fixtures['F00003']
    with pytest.raises(AssertionError):
        checker.validate_origin(s,f,1,'PROCESS_CRASH_BEFORE','exact-survivor',[],checker.normal_call_snapshots(f),d['byte_blobs'])


def m4_namespace_origins(d,origins,fixtures,fault):
    for o in origins.values():
        f=fixtures[o['fixture_id']];call=f['calls'][o['call_ordinal']-1]
        if o['failure_mode']==fault and (call['role']=='full_controlled_namespace_plus_protected_custody' or call['action'] in ('read_complete_index_tree_worktree','verify_full_status_and_custody')):
            yield o,f,call,d['components'][o['fault_operations']]


def test_m4_role_aware_content_fault_uses_regular_descendant(m4_inventory,m4_indexes):
    d=m4_inventory;_,origins,fixtures=m4_indexes;found=0
    for o,f,call,ops in m4_namespace_origins(d,origins,fixtures,'CONTENT_HASH_MISMATCH'):
        target=o['fault_target'];snap=d['components'][f['initial_frame']['actual_snapshot']]
        ns=d['components'][snap['namespace']];ins=d['components'][snap['inodes']]
        assert target['namespace_scope_anchor']=='/opt/aios-src' and target['concrete_fault_target'].startswith('/opt/aios-src/')
        assert target['witness_role']=='regular_content' and ins[ns[target['concrete_fault_target']]]['file_type']=='regular'
        assert ops==[{'syscall':'ftruncate_write','path':target['concrete_fault_target'],'sha256':ops[0]['sha256']}];found+=1
    assert found==33


def test_m4_role_aware_alias_fault_uses_regular_descendant(m4_inventory,m4_indexes):
    d=m4_inventory;_,origins,fixtures=m4_indexes;found=0
    for o,f,call,ops in m4_namespace_origins(d,origins,fixtures,'UNEXPECTED_ALIAS'):
        target=o['fault_target'];assert target['witness_role']=='regular_hardlink_source'
        snap=d['components'][f['initial_frame']['actual_snapshot']];ns=d['components'][snap['namespace']]
        assert d['components'][snap['inodes']][ns[target['concrete_fault_target']]]['file_type']=='regular'
        assert ops[0]['syscall']=='linkat' and ops[0]['source']==target['concrete_fault_target']!=target['namespace_scope_anchor'];found+=1
    assert found==32


@pytest.mark.parametrize('fault',['WRONG_MODE','WRONG_OWNER','WRONG_GROUP'])
def test_m4_role_aware_metadata_uses_concrete_child(fault,m4_inventory,m4_indexes):
    d=m4_inventory;_,origins,fixtures=m4_indexes;found=0
    for o,f,call,ops in m4_namespace_origins(d,origins,fixtures,fault):
        target=o['fault_target'];assert target['witness_role']=='regular_metadata'
        assert target['concrete_fault_target'].startswith(target['namespace_scope_anchor']+'/')
        assert ops[0]['path']==target['concrete_fault_target'] and ops[0]['syscall']==('fchmod' if fault=='WRONG_MODE' else 'fchown');found+=1
    assert found==32


def test_m4_scope_anchor_is_not_accidentally_mutated(m4_inventory,m4_indexes):
    d=m4_inventory;cases,origins,fixtures=m4_indexes;found=0
    for o in origins.values():
        f=fixtures[o['fixture_id']];call=f['calls'][o['call_ordinal']-1]
        whole=call['action'] in ('verify_phase_namespace_and_git','read_complete_index_tree_worktree','verify_full_status_and_custody','verify_terminal')
        if not whole or o['outcome_variant']!='assigned' or o['failure_mode'] in ('CUSTODY_LOST','REVOKED','SERVICE_IDENTITY_CHANGED','AUTH_CUSTODY_CHANGED'):continue
        target=o['fault_target'];assert target is not None
        scope=target['namespace_scope_anchor'];assert scope==call['path'] and target['concrete_fault_target']!=scope
        before=d['components'][f['initial_frame']['actual_snapshot']]
        state=d['states'][cases[o['case_id']]['semantic_state_fingerprint']];after=d['components'][state['actual_snapshot']]
        bns,ans=d['components'][before['namespace']],d['components'][after['namespace']]
        assert bns[scope]==ans[scope]
        assert d['components'][before['inodes']][bns[scope]]==d['components'][after['inodes']][ans[scope]]
        found+=1
    assert found


@pytest.mark.parametrize('fault',['WRONG_OWNER','WRONG_GROUP','WRONG_MODE','CONCURRENT_NAMESPACE_REPLACEMENT','LINK_COUNT_MISMATCH','CORRUPTED_OBJECT','SYMLINK_COMPONENT'])
def test_m4_missing_object_binding_is_coverage_obligation(fault,m4_inventory):
    found=0
    for row in m4_inventory['candidate_exclusions']:
        if row.get('call',{}).get('path')!='release://approved-object-stream' or row.get('failure_mode')!=fault:continue
        assert row['classification']=='UNBOUND_COVERAGE_OBLIGATION'
        assert row['required_binding']['witness_role'] and row['fixture_id'] and row['program_sha256']
        assert row['accepted_coverage'] is False and row['filesystem_impossibility'] is False;found+=1
    assert found


@pytest.mark.parametrize('reason',['traversal root cannot be replaced','held descriptor inode cannot change file type'])
def test_m4_actual_impossibilities_keep_filesystem_category(reason,m4_inventory):
    rows=[e for e in m4_inventory['candidate_exclusions'] if e['reason']==reason]
    assert rows and all(e['classification']=='INVALID_FILESYSTEM_REALIZABILITY' for e in rows)


def test_m4_all_unbound_obligations_are_retained_and_not_accepted(m4_inventory,m4_indexes):
    d=m4_inventory;_,origins,_=m4_indexes;rows=[e for e in d['candidate_exclusions'] if e['classification']=='UNBOUND_COVERAGE_OBLIGATION']
    assert len(rows)==d['unbound_coverage_obligations'] and rows
    for row in rows:
        assert row['origin_fault_site_id'] not in origins and row['required_binding']
        assert row['reason'] and row['accepted_coverage'] is False and row['filesystem_impossibility'] is False
    assert not any('unavailable' in e['reason'].lower() or 'not bound' in e['reason'].lower() for e in d['candidate_exclusions'] if e['classification']=='INVALID_FILESYSTEM_REALIZABILITY')


def test_m4_previously_excluded_namespace_faults_are_accepted(m4_inventory,m4_indexes):
    _,origins,fixtures=m4_indexes;found=0;excluded={e['origin_fault_site_id'] for e in m4_inventory['candidate_exclusions']}
    for f in fixtures.values():
        for i,c in enumerate(f['calls'],1):
            faults=['CONTENT_HASH_MISMATCH','UNEXPECTED_ALIAS'] if c['action']=='verify_phase_namespace_and_git' else ['CONTENT_HASH_MISMATCH'] if c['action']=='read_complete_index_tree_worktree' else []
            for fault in faults:
                key=f"{f['id']}:call{i:03d}:{fault}:assigned"
                assert key in origins and key not in excluded;found+=1
    assert found==65


def test_m4_fingerprint_excludes_witness_annotations(m4_inventory):
    forbidden={'fault_target','scope_anchor','namespace_scope_anchor','concrete_fault_target','witness_role','required_binding','proof_base','pending_ledger_file'}
    for state in m4_inventory['states'].values():assert not forbidden & set(state)


@pytest.mark.parametrize('operation',['symlink_hardlink','mixed_exchange'])
def test_m4_unbound_valid_endpoint_contract_is_not_impossible(operation,m4_compiler):
    directory={'dev':1,'ino':1,'uid':1000,'gid':1000,'mode':0o700,'file_type':'directory','outside_links':2,'content':None}
    regular={**directory,'ino':2,'mode':0o600,'file_type':'regular','outside_links':0,'content':{'sha256':hashlib.sha256(b'x').hexdigest()}}
    symlink={**regular,'ino':3,'mode':0o777,'file_type':'symlink','content':{'target':'/file'}}
    ns={'/':'root','/file':'file','/sym':'sym'};ins={'root':directory,'file':regular,'sym':symlink}
    ops=[{'syscall':'linkat','source':'/sym','path':'/alias'}] if operation=='symlink_hardlink' else [{'syscall':'renameat2_EXCHANGE','source':'/file','path':'/sym'}]
    with pytest.raises(m4_compiler.UnboundCoverage):m4_compiler.replay_fault_operations(ns,ins,ops)



def test_m4_independent_validator_rejects_nonsemantic_annotation(m4_inventory,m4_compiler):
    d=m4_inventory;state=copy.deepcopy(next(iter(d['states'].values())))
    state['required_binding']={'representative_scope':'/opt/aios-src'}
    checker=m4_compiler.OutcomeAudit(P,d['components'],d['bound_inputs']);checker.catalog=d['record_catalog']
    with pytest.raises(AssertionError,match='nonsemantic state annotation'):checker.validate_outcome(state)


# M4 final witness/precedence correction: prepared only, never executed here.
def m4_target_checker(d, module):
    checker=module.OutcomeAudit(P,d['components'],d['bound_inputs'])
    checker.catalog=d['record_catalog']
    return checker


def test_m4_every_mutation_origin_has_capable_concrete_target(m4_inventory,m4_indexes,m4_compiler):
    # Derive required capabilities from actual syscalls, not the selector's labels.
    d=m4_inventory;_,origins,fixtures=m4_indexes
    checker=m4_target_checker(d,m4_compiler);normal={};found=0
    for o in origins.values():
        ops=d['components'][o['fault_operations']];partial=o['outcome_variant'].startswith('prefix-')
        if not ops and not partial:continue
        t=o['fault_target'];assert isinstance(t,dict)
        f=fixtures[o['fixture_id']];call=f['calls'][o['call_ordinal']-1]
        if f['id'] not in normal:normal[f['id']]=checker.normal_call_snapshots(f)
        before=normal[f['id']][o['call_ordinal']-1][0];ns,ins=checker.filesystem_view(before)
        path=t['concrete_fault_target'];inode=ins.get(ns.get(path));kind=inode['file_type'] if inode else None
        assert t['predicate']==o['failure_mode'] and t['witness_role']
        role=t['witness_role']
        if role in ('regular_content','git_object_content','regular_hardlink_source','regular_metadata',
                    'regular_replacement','regular_symlink_replacement','regular_removal'):
            assert kind=='regular'
        elif role=='directory_replacement':assert kind=='directory'
        elif role in ('metadata_object','link_count_object'):assert kind in ('regular','directory')
        elif role in ('exclusive_creation_path','ledger_file_creation'):assert inode is None
        else:assert role in ('replaceable_path','symlink_replaceable_path')
        if partial:
            assert path==call['path'] and kind=='regular'
        else:
            last=ops[-1]
            if last['syscall']=='linkat':
                assert path==last['source'] and kind=='regular'
                assert inode['dev']==ins[ns[str(Path(last['path']).parent)]]['dev']
            elif o['failure_mode']=='LINK_COUNT_MISMATCH':
                assert last['syscall']=='mkdirat' and str(Path(last['path']).parent)==path and kind=='directory'
            else:assert path==last['path']
            if last['syscall']=='ftruncate_write':assert kind=='regular' and inode['content']['sha256']
            if last['syscall'] in ('fchmod','fchown'):assert kind in ('regular','directory')
            if last['syscall']=='unlinkat':assert kind=='regular'
        scope=t['namespace_scope_anchor']
        if scope is not None:
            assert scope==call['path'] and path!=scope
            assert all(x['path']!=scope and x.get('source')!=scope for x in ops)
        found+=1
    assert found and found==sum(bool(d['components'][o['fault_operations']]) or o['outcome_variant'].startswith('prefix-') for o in origins.values())


@pytest.mark.parametrize('fault',['CONTENT_HASH_MISMATCH','SAME_HASH_FOREIGN_INODE','PARTIAL_WRITE_THEN_EIO'])
def test_m4_acceptance_rejects_null_mutation_target(fault,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;cases,origins,fixtures=m4_indexes
    o=next(o for o in origins.values() if o['failure_mode']==fault and o['fault_target'] is not None)
    f=fixtures[o['fixture_id']];s=d['states'][cases[o['case_id']]['semantic_state_fingerprint']]
    checker=m4_target_checker(d,m4_compiler)
    with pytest.raises(AssertionError,match='mutation fault requires a concrete target'):
        checker.validate_origin(s,f,o['call_ordinal'],fault,o['outcome_variant'],
                                d['components'][o['fault_operations']],checker.normal_call_snapshots(f),d['byte_blobs'],None)


@pytest.mark.parametrize('forgery',['scope_as_target','wrong_scope','wrong_role'])
def test_m4_acceptance_rejects_scope_and_role_substitution(forgery,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;cases,origins,fixtures=m4_indexes
    o=origins['F01964:call006:SAME_HASH_FOREIGN_INODE:assigned'];f=fixtures[o['fixture_id']]
    t=copy.deepcopy(o['fault_target'])
    if forgery=='scope_as_target':t['concrete_fault_target']=t['namespace_scope_anchor']
    elif forgery=='wrong_scope':t['namespace_scope_anchor']='/opt'
    else:t['witness_role']='directory_replacement'
    checker=m4_target_checker(d,m4_compiler);s=d['states'][cases[o['case_id']]['semantic_state_fingerprint']]
    with pytest.raises((AssertionError,m4_compiler.InvalidFilesystem)):
        checker.validate_origin(s,f,o['call_ordinal'],o['failure_mode'],o['outcome_variant'],
                                d['components'][o['fault_operations']],checker.normal_call_snapshots(f),d['byte_blobs'],t)


def test_m4_full_status_same_hash_fault_replaces_concrete_regular_file(m4_inventory,m4_indexes):
    d=m4_inventory;cases,origins,fixtures=m4_indexes
    o=origins['F01964:call006:SAME_HASH_FOREIGN_INODE:assigned'];f=fixtures[o['fixture_id']]
    t=o['fault_target'];path=t['concrete_fault_target'];scope=t['namespace_scope_anchor']
    assert scope=='/opt/aios-src' and path.startswith(scope+'/')
    assert t['witness_role']=='regular_replacement'
    b=d['components'][f['initial_frame']['actual_snapshot']]
    a=d['components'][d['states'][cases[o['case_id']]['semantic_state_fingerprint']]['actual_snapshot']]
    bns,ans=d['components'][b['namespace']],d['components'][a['namespace']]
    bi,ai=d['components'][b['inodes']][bns[path]],d['components'][a['inodes']][ans[path]]
    assert bi['file_type']==ai['file_type']=='regular' and bi['content']==ai['content']
    assert (bi['dev'],bi['ino'])!=(ai['dev'],ai['ino'])
    assert bns[scope]==ans[scope]
    assert d['components'][b['inodes']][bns[scope]]==d['components'][a['inodes']][ans[scope]]
    assert [x['syscall'] for x in d['components'][o['fault_operations']]]==['create_file','renameat2_REPLACE']


@pytest.mark.parametrize('fault',['CONTENT_HASH_MISMATCH','UNEXPECTED_ALIAS'])
def test_m4_namespace_without_eligible_child_is_unbound(fault,m4_compiler):
    call={'action':'verify_phase_namespace_and_git','role':'full_controlled_namespace_plus_protected_custody','path':'/opt/aios-src'}
    directory={'dev':2049,'uid':1000,'gid':1000,'mode':0o755,'file_type':'directory','outside_links':2,'content':None}
    ns={'/':'root','/opt':'opt','/opt/aios-src':'scope'}
    ins={token:{**directory,'ino':i} for i,token in enumerate(('root','opt','scope'),1)}
    assert m4_compiler.validate_filesystem(ns,ins) is True
    with pytest.raises(m4_compiler.UnboundCoverage) as caught:
        m4_compiler.namespace_witness(P,ns,ins,fault,call)
    assert caught.value.required_binding['namespace_scope_anchor']==call['path']
    assert caught.value.required_binding['required_type']=='regular'


@pytest.mark.parametrize('binding',['staging','release_stream'])
def test_m4_held_type_impossibility_precedes_object_binding(binding,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;_,_,fixtures=m4_indexes
    f=fixtures['F00242' if binding=='staging' else 'F00230']
    call=next(c for c in f['calls'] if c['action']=='fstat_verify_regular')
    c=m4_compiler.Compiler(P);c.components=dict(d['components']);c.records=d['record_catalog']
    c.audit=m4_compiler.OutcomeAudit(P,c.components,d['bound_inputs']);c.audit.catalog=c.records
    frame={**f['initial_frame'],'ledger_files_override':f['initial_frame']['ledger_files']}
    with pytest.raises(m4_compiler.InvalidFilesystem,match='held descriptor inode cannot change file type'):
        c.corrupt(frame,'WRONG_TYPE',call)


def test_m4_every_held_type_fault_is_physical_impossibility(m4_inventory,m4_indexes):
    d=m4_inventory;_,origins,fixtures=m4_indexes
    rejected={e['origin_fault_site_id']:e for e in d['candidate_exclusions']};object_count=0
    for f in fixtures.values():
        for i,call in enumerate(f['calls'],1):
            if not call['action'].startswith('fstat_'):continue
            key=f"{f['id']}:call{i:03d}:WRONG_TYPE:assigned"
            assert key not in origins
            row=rejected[key]
            assert row['classification']=='INVALID_FILESYSTEM_REALIZABILITY'
            assert row['reason']=='held descriptor inode cannot change file type'
            object_count+=call['role']=='object'
    assert object_count==248


def test_m4_held_regular_object_corruption_remains_accepted(m4_inventory,m4_indexes):
    d=m4_inventory;cases,origins,fixtures=m4_indexes;found=0
    for f in fixtures.values():
        for i,call in enumerate(f['calls'],1):
            if call['action']!='read_and_strict_zlib_decode' or not call['path'].startswith('/'):continue
            assert f['calls'][i-2]['action']=='fstat_verify_regular'
            o=origins[f"{f['id']}:call{i:03d}:CORRUPTED_OBJECT:assigned"]
            t=o['fault_target'];assert t['concrete_fault_target']==call['path'] and t['witness_role']=='git_object_content'
            b=d['components'][f['initial_frame']['actual_snapshot']]
            a=d['components'][d['states'][cases[o['case_id']]['semantic_state_fingerprint']]['actual_snapshot']]
            bns,ans=d['components'][b['namespace']],d['components'][a['namespace']]
            bi,ai=d['components'][b['inodes']][bns[call['path']]],d['components'][a['inodes']][ans[call['path']]]
            assert bns[call['path']]==ans[call['path']]
            assert bi['file_type']==ai['file_type']=='regular' and bi['content']!=ai['content']
            assert (bi['dev'],bi['ino'])==(ai['dev'],ai['ino']);found+=1
    assert found==62


def test_m4_unbound_obligations_follow_physical_precheck(m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;_,origins,fixtures=m4_indexes;checker=m4_target_checker(d,m4_compiler);normal={};found=0
    for row in d['candidate_exclusions']:
        if row['classification']!='UNBOUND_COVERAGE_OBLIGATION':continue
        f=fixtures[row['fixture_id']];call=row['call']
        assert not (call['action'].startswith('fstat_') and row['failure_mode']=='WRONG_TYPE')
        assert row['origin_fault_site_id'] not in origins and row['required_binding']
        if f['id'] not in normal:normal[f['id']]=checker.normal_call_snapshots(f)
        assert row['physical_realizability_precheck']==checker.unbound_precheck(
            f,row['call_ordinal'],row['failure_mode'],row['outcome_variant'],normal[f['id']])
        assert row['physical_realizability_precheck']['status']=='PASSED_CONDITIONAL_REALIZABILITY'
        if call['path']=='release://approved-object-stream' and row['failure_mode']=='CORRUPTED_OBJECT':found+=1
    assert found


@pytest.mark.parametrize('binding',['staging','release_stream'])
def test_m4_audit_rejects_impossible_object_as_unbound(binding,m4_inventory,m4_indexes,m4_compiler):
    d=m4_inventory;_,_,fixtures=m4_indexes;f=fixtures['F00242' if binding=='staging' else 'F00230']
    i=next(i for i,c in enumerate(f['calls'],1) if c['action']=='fstat_verify_regular')
    checker=m4_target_checker(d,m4_compiler)
    with pytest.raises(m4_compiler.InvalidFilesystem,match='held descriptor inode cannot change file type'):
        checker.unbound_precheck(f,i,'WRONG_TYPE','assigned',checker.normal_call_snapshots(f))
