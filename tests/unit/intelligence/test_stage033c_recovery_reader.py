"""Offline local proof only; independent operator authorization stays external.

Synthetic root custody and Git histories do not attest live human review.
No production paths are read and no installation is executed by these tests.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[3]
EXECUTOR = ROOT / 'docs/intelligence/stage-0.33c-step4-one-shot-runtime-install-authority/one_shot_install.py'
spec = importlib.util.spec_from_file_location('recovery_reader_test_executor', EXECUTOR)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode() + b'\n'


def activation():
    return dict(schema_version=m.ACTIVATION_SCHEMA_VERSION, authority_id=m.AUTHORITY_ID,
                expected_runtime_head='a'*40, executor_sha256='b'*64,
                policy_reference=str(m.REL_POLICY), approval_id=m.RECOVERY_APPROVAL_ID,
                package_payload_sha256=m.RECOVERY_PAYLOAD_SHA256,
                activated_at_utc='2026-09-27T01:00:00.000000Z')


def selector():
    return dict(schema_version='aios-p4s7-recovery-review-merge-trust-v1',
                evidence_commit='a'*40, evidence_path=m.EVIDENCE_PREFIX+'12345678-1234-1234-1234-123456789abc.json',
                evidence_transport_sha256='b'*64)


def evidence():
    review = dict(pr_number=302, reviewed_head_sha='a'*40, merge_sha='b'*40)
    return dict(schema_version='aios-p4s7-recovery-review-merge-evidence-v1', repository='bader5657/AIOS',
                binding_id='12345678-1234-1234-1234-123456789abc', authority_id=m.AUTHORITY_ID,
                policy_reference=str(m.REL_POLICY), activation_governance_reference=str(m.REL_R34),
                approval_id=m.RECOVERY_APPROVAL_ID, package_payload_sha256=m.RECOVERY_PAYLOAD_SHA256,
                expected_runtime_head='a'*40, executor_sha256='b'*64, policy_sha256='c'*64,
                reader=review, r32=dict(pr_number=299, reviewed_head_sha='a'*40, merge_sha=m.R32_MERGE),
                r34=dict(pr_number=300, reviewed_head_sha='a'*40, merge_sha=m.R34_MERGE),
                supersedes=dict(kind='r34-baseline', commit=m.R34_MERGE, path=str(m.REL_R34), transport_sha256='d'*64))


def validate(kind, value):
    if kind == 'activation':
        m.validate_activation_schema(value, 'b'*64)
    elif kind == 'selector':
        m.validate_selector(value)
    else:
        m.validate_evidence(value, selector()['evidence_path'])


BUILDERS = {'activation': activation, 'selector': selector, 'evidence': evidence}


@pytest.mark.parametrize('kind', BUILDERS)
def test_valid_closed_canonical_record(kind):
    value = BUILDERS[kind]()
    validate(kind, m.canonical_record(canonical(value), 'TEST'))


@pytest.mark.parametrize('kind,key', [(k, f) for k,b in BUILDERS.items() for f in b()])
@pytest.mark.parametrize('mutation', ['missing', 'null', 'array', 'bool', 'int', 'float'])
def test_every_field_closed_types(kind, key, mutation):
    value = BUILDERS[kind]()
    if mutation == 'missing':
        del value[key]
    else:
        value[key] = dict(null=None, array=[], bool=True, int=1, float=1.0)[mutation]
    with pytest.raises(m.Stop) as caught:
        validate(kind, value)
    assert caught.value.classification == m.PRECONDITION_FAILED


@pytest.mark.parametrize('kind', BUILDERS)
@pytest.mark.parametrize('mutation', ['extra', 'duplicate', 'bom', 'crlf', 'double_lf', 'missing_lf', 'pretty', 'reordered', 'space', 'malformed', 'utf8', 'nan'])
def test_bad_transport(kind, mutation):
    value = BUILDERS[kind]()
    data = canonical(value)
    if mutation == 'extra':
        value['extra'] = 'no'; data = canonical(value)
    elif mutation == 'duplicate':
        key = next(iter(value)); data = b'{'+json.dumps(key).encode()+b':null,'+data[1:]
    elif mutation == 'bom': data = b'\xef\xbb\xbf'+data
    elif mutation == 'crlf': data = data[:-1]+b'\r\n'
    elif mutation == 'double_lf': data += b'\n'
    elif mutation == 'missing_lf': data = data[:-1]
    elif mutation == 'pretty': data = json.dumps(value, indent=2).encode()+b'\n'
    elif mutation == 'reordered': data = json.dumps(value, separators=(',', ':')).encode()+b'\n'
    elif mutation == 'space': data = b' '+data
    elif mutation == 'malformed': data = b'{\n'
    elif mutation == 'utf8': data = b'{"x":"\xff"}\n'
    elif mutation == 'nan': data = b'{"x":NaN}\n'
    with pytest.raises(m.Stop):
        validate(kind, m.canonical_record(data, 'TEST'))


@pytest.mark.parametrize('name', ['reader', 'r32', 'r34', 'supersedes'])
@pytest.mark.parametrize('mutation', ['missing', 'extra', 'duplicate', 'wrong_type'])
def test_nested_objects_closed(name, mutation):
    value = evidence()
    key = next(iter(value[name]))
    if mutation == 'missing': del value[name][key]
    elif mutation == 'extra': value[name]['extra'] = 'no'
    elif mutation == 'wrong_type': value[name][key] = True
    data = canonical(value)
    if mutation == 'duplicate':
        marker = ('"'+name+'":{').encode()
        data = data.replace(marker, marker+json.dumps(key).encode()+b':null,')
    with pytest.raises(m.Stop):
        validate('evidence', m.canonical_record(data, 'TEST'))


class Graph:
    def __init__(self, root, monkeypatch):
        self.repo = root/'repo'; self.repo.mkdir()
        self.serial = 0
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Synthetic review fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.write('initial', b'fixture\n'); self.commit()
        historical = b'historical executor\n'
        self.r32 = self.merge({m.REL_EXECUTOR: historical, m.REL_POLICY: self.policy(historical), m.REL_R32: b'R32 fixture\n'})
        monkeypatch.setattr(m, 'R32_MERGE', self.r32['merge_sha'])
        self.r34 = self.merge({m.REL_R34: b'R34 fixture\n'})
        monkeypatch.setattr(m, 'R34_MERGE', self.r34['merge_sha'])
        contract = b'synthetic frozen trust contract\n'
        trust = self.merge({m.REL_TRUST: contract})
        monkeypatch.setattr(m, 'TRUST_MERGE', trust['merge_sha'])
        monkeypatch.setattr(m, 'TRUST_SHA256', m.sha256(contract))
        self.executor = b'amended recovery executor\n'
        self.reader = self.merge({m.REL_EXECUTOR: self.executor, m.REL_POLICY: self.policy(self.executor)})
        self.head = self.reader['merge_sha']
        self.record = evidence()
        self.record.update(r32={**self.r32, 'pr_number':299}, r34={**self.r34, 'pr_number':300},
                           reader={**self.reader, 'pr_number':302}, expected_runtime_head=self.head,
                           executor_sha256=m.sha256(self.executor), policy_sha256=m.sha256(self.policy(self.executor)),
                           supersedes=dict(kind='r34-baseline', commit=m.R34_MERGE, path=str(m.REL_R34),
                                           transport_sha256=m.sha256(b'R34 fixture\n')))
        self.act = activation(); self.act.update(expected_runtime_head=self.head, executor_sha256=m.sha256(self.executor))
        self.sel = self.publish(self.record)
        self.git('checkout', '--detach', self.head)
        monkeypatch.setattr(m, 'utc_now', lambda: m.parse_utc('2026-09-27T01:30:00.000000Z'))
        monkeypatch.setattr(m, 'REPOSITORY', self.repo)
        monkeypatch.setattr(m, 'check_no_args_root', lambda: None)
        monkeypatch.setattr(m, '_protected_record', self.protected)

    def policy(self, code):
        return (m.AUTHORITY_ID+'\nP4S6_BLOCKERS_REMEDIATED_READY_FOR_REREVIEW\n| executor SHA-256 | `'+m.sha256(code)+'` |\n').encode()

    def git(self, *args):
        return subprocess.check_output(['git','-C',str(self.repo),*map(str,args)], stderr=subprocess.DEVNULL).decode().strip()

    def write(self, path, data):
        p=self.repo/path; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(data)

    def commit(self):
        self.git('add','.'); self.git('commit','-m','synthetic fixture'); return self.git('rev-parse','HEAD')

    def merge(self, files, base=None, merge_change=None):
        self.serial += 1
        if base: self.git('checkout','--detach',base)
        base=self.git('rev-parse','HEAD')
        self.git('checkout','-b',f'fixture-{self.serial}')
        for path, data in files.items(): self.write(path,data)
        reviewed=self.commit()
        self.git('checkout','--detach',base)
        self.git('merge','--no-ff','--no-commit',reviewed)
        if merge_change:
            for path,data in merge_change.items(): self.write(path,data)
        merged=self.commit()
        return dict(pr_number=302, reviewed_head_sha=reviewed, merge_sha=merged)

    def publish(self, record, base=None, raw=None, extra=None):
        path=m.EVIDENCE_PREFIX+record['binding_id']+'.json'
        data=raw if raw is not None else canonical(record)
        files={path:data}; files.update(extra or {})
        identity=self.merge(files, base=base or self.head)
        return dict(schema_version='aios-p4s7-recovery-review-merge-trust-v1', evidence_commit=identity['merge_sha'],
                    evidence_path=path, evidence_transport_sha256=m.sha256(data))

    def protected(self, path, stage):
        if path == m.ACTIVATION_RECORD: return canonical(self.act)
        if path == m.TRUST_SELECTOR: return canonical(self.sel)
        raise AssertionError('unexpected protected path')

    def republish(self, record=None, **kwargs):
        self.sel=self.publish(record or self.record, **kwargs)
        self.git('checkout','--detach',self.head)

    def verify(self): return m.verify_merged_authority(m.sha256(self.executor), m.read_activation_record())

    def assert_stop(self):
        with ExitStack() as stack:
            spies=[stack.enter_context(patch.object(m,name,side_effect=AssertionError('past trust gate: '+name)))
                   for name in ('read_source','durable_claim','stage_and_publish','write_failure_result','open_dir')]
            publication=stack.enter_context(patch.object(m.os,'link',side_effect=AssertionError('publication')))
            with pytest.raises(m.GovernedStop) as caught: m.main()
            assert caught.value.classification == m.PRECONDITION_FAILED
            for spy in spies+[publication]: spy.assert_not_called()
        return caught.value


@pytest.fixture
def graph(tmp_path, monkeypatch):
    return Graph(tmp_path, monkeypatch)


def test_authenticated_chain_passes_all_local_trust_gates(graph):
    assert graph.verify() == graph.reader['merge_sha']
    # External operator verification is an independent procedural prerequisite,
    # not simulated by a new reader input. Stop before opening private sources.
    class ReachedInterpreter(Exception): pass
    with patch.object(m,'verify_actual_interpreter',side_effect=ReachedInterpreter), patch.object(m,'read_source') as source:
        with pytest.raises(ReachedInterpreter): m.main()
        source.assert_not_called()


@pytest.mark.parametrize('field', ['authority_id','approval_id','package_payload_sha256','expected_runtime_head','executor_sha256','policy_reference','schema_version'])
def test_activation_wrong_binding_main_zero_effects(graph, field):
    graph.act[field]='f'*len(graph.act[field]); graph.assert_stop()


@pytest.mark.parametrize('field', ['repository','authority_id','approval_id','package_payload_sha256','policy_reference','activation_governance_reference','expected_runtime_head','executor_sha256','policy_sha256','schema_version'])
def test_evidence_wrong_binding_main_zero_effects(graph, field):
    record=copy.deepcopy(graph.record); record[field]='f'*len(record[field])
    graph.republish(record); graph.assert_stop()


@pytest.mark.parametrize('component', ['r32','r34','reader'])
@pytest.mark.parametrize('field', ['pr_number','reviewed_head_sha','merge_sha'])
def test_review_identity_failures(graph, component, field):
    record=copy.deepcopy(graph.record)
    record[component][field] = 299 if field=='pr_number' else 'f'*40
    if component=='r32' and field=='pr_number': record[component][field]=300
    graph.republish(record); graph.assert_stop()


@pytest.mark.parametrize('field,value', [('evidence_commit','f'*40),('evidence_path','../escape'),('evidence_transport_sha256','f'*64),('schema_version','wrong')])
def test_selector_wrong_binding(graph, field, value):
    graph.sel[field]=value; graph.assert_stop()


@pytest.mark.parametrize('raw', [b'{\n', b'{}\n', b'{"x":1,"x":2}\n', b'{ "x":1}\n'])
def test_bad_evidence_transport_main_zero_effects(graph, raw):
    graph.republish(raw=raw); graph.assert_stop()


@pytest.mark.parametrize('which', ['activation','selector'])
@pytest.mark.parametrize('failure', ['absent','malformed','extra','missing','duplicate','noncanonical'])
def test_protected_input_failures_main_zero_effects(graph, monkeypatch, which, failure):
    target=m.ACTIVATION_RECORD if which=='activation' else m.TRUST_SELECTOR
    original=graph.protected
    def read(path,stage):
        if path != target: return original(path,stage)
        if failure=='absent': raise m.Stop(m.PRECONDITION_FAILED,stage)
        data=json.loads(original(path,stage))
        if failure=='malformed': return b'{\n'
        if failure=='extra': data['extra']='x'
        if failure=='missing': del data['schema_version']
        if failure=='duplicate': return b'{"schema_version":"x",'+canonical(data)[1:]
        if failure=='noncanonical': return b' '+canonical(data)
        return canonical(data)
    monkeypatch.setattr(m,'_protected_record',read); graph.assert_stop()


@pytest.mark.parametrize('field', ['commit','path','transport_sha256','kind'])
def test_wrong_predecessor(graph, field):
    record=copy.deepcopy(graph.record); record['supersedes'][field]='f'*40
    graph.republish(record); graph.assert_stop()


def test_second_record_chain_positive(graph):
    first=graph.sel.copy(); record=copy.deepcopy(graph.record)
    record['binding_id']='22345678-1234-1234-1234-123456789abc'
    record['supersedes']=dict(kind='recovery-evidence-v1',commit=first['evidence_commit'],path=first['evidence_path'],transport_sha256=first['evidence_transport_sha256'])
    graph.republish(record,base=first['evidence_commit'])
    assert graph.verify()==graph.reader['merge_sha']


def test_skipped_predecessor_rejected(graph):
    first=graph.sel.copy(); record=copy.deepcopy(graph.record)
    record['binding_id']='22345678-1234-1234-1234-123456789abc'
    # Claims baseline predecessor although first record is in authenticated history.
    graph.republish(record,base=first['evidence_commit']); graph.assert_stop()


def test_conflicting_successor_same_merge_rejected(graph):
    graph.republish(extra={m.EVIDENCE_PREFIX+'22345678-1234-1234-1234-123456789abc.json':canonical(graph.record)})
    graph.assert_stop()


def test_predecessor_from_unrelated_branch_rejected(graph):
    first=graph.sel.copy(); record=copy.deepcopy(graph.record)
    record['binding_id']='22345678-1234-1234-1234-123456789abc'
    record['supersedes']=dict(kind='recovery-evidence-v1',commit=first['evidence_commit'],path=first['evidence_path'],transport_sha256=first['evidence_transport_sha256'])
    graph.republish(record,base=graph.head); graph.assert_stop()


def test_cyclic_binding_id_rejected(graph):
    # Reusing the selected binding identity for a predecessor is a locally
    # observable cycle/conflict even before following additional links.
    first=graph.sel.copy(); record=copy.deepcopy(graph.record)
    record['supersedes']=dict(kind='recovery-evidence-v1',commit=first['evidence_commit'],path=first['evidence_path'],transport_sha256=first['evidence_transport_sha256'])
    graph.republish(record,base=first['evidence_commit']); graph.assert_stop()


@pytest.mark.parametrize('kind', ['tracked','staged','untracked','wrong_head','executor_hidden','policy_hidden'])
def test_runtime_drift_zero_effects(graph,kind):
    if kind=='wrong_head': graph.git('checkout','--detach',m.R34_MERGE)
    elif kind in ('executor_hidden','policy_hidden'):
        path=m.REL_EXECUTOR if kind=='executor_hidden' else m.REL_POLICY
        graph.git('update-index','--assume-unchanged',path); graph.write(path,b'changed\n')
    else:
        path='untracked' if kind=='untracked' else 'initial'; graph.write(path,b'changed\n')
        if kind=='staged': graph.git('add',path)
    graph.assert_stop()


@pytest.mark.parametrize('byte_helper', [False,True])
def test_git_errors_fail_closed(graph,byte_helper):
    assert graph.verify()==graph.reader['merge_sha']
    helper='_git_bytes' if byte_helper else 'run_git'
    with patch.object(m,helper,side_effect=m.Stop(m.PRECONDITION_FAILED,'RUNTIME_REPOSITORY')):
        graph.assert_stop()


def test_selector_changes_during_verification(graph,monkeypatch):
    original=graph.protected; count=0
    def changing(path,stage):
        nonlocal count
        if path==m.TRUST_SELECTOR:
            count+=1
            if count>1: return b'{}\n'
        return original(path,stage)
    monkeypatch.setattr(m,'_protected_record',changing); graph.assert_stop()


def test_offline_revocation_is_indistinguishable_no_invented_gate(graph):
    before=graph.verify()
    # An unavailable external revocation changes NO local input. No fake
    # receipt/flag is introduced; the external operator must block execution.
    after=graph.verify()
    assert before==after
    assert 'Fresh independent operator verification is EXTERNAL' in m.read_recovery_evidence.__doc__
    assert set(graph.sel)==m.SELECTOR_KEYS
    assert set(graph.act)==m.ACTIVATION_KEYS


@pytest.mark.parametrize('case', ['valid','missing','symlink','directory','mode','uid','gid','nlink','unsafe_parent','changed_identity'])
def test_real_selector_custody(tmp_path, case):
    import stat
    parent=tmp_path/'custody'; parent.mkdir(mode=0o750)
    path=parent/'selector'; data=canonical(selector())
    path.write_bytes(data); path.chmod(0o400)
    if case=='missing': path.unlink()
    elif case=='symlink':
        original=parent/'original'; path.rename(original); path.symlink_to(original)
    elif case=='directory': path.unlink(); path.mkdir()
    elif case=='mode': path.chmod(0o600)
    elif case=='nlink': os.link(path,parent/'hardlink')
    real_fstat,real_stat=os.fstat,os.stat
    group=os.getgid()
    def info(raw, is_entry=False):
        attrs={k:getattr(raw,k) for k in dir(raw) if k.startswith('st_')}
        if stat.S_ISDIR(raw.st_mode):
            attrs.update(st_uid=0,st_gid=group,st_mode=stat.S_IFDIR|0o750)
            if case=='unsafe_parent': attrs['st_mode']=stat.S_IFDIR|0o777
        else:
            attrs.update(st_uid=1000 if case=='uid' else 0,st_gid=1000 if case=='gid' else 0)
            if case=='changed_identity' and is_entry: attrs['st_ino']+=1
        return SimpleNamespace(**attrs)
    # Only custody identities are synthesized for unprivileged CI. File opens,
    # no-follow behavior, descriptors, bytes, link count and file mode are real.
    with patch.object(m.os,'fstat',side_effect=lambda fd:info(real_fstat(fd))), \
         patch.object(m.os,'stat',side_effect=lambda *a,**kw:info(real_stat(*a,**kw),True)), \
         patch.object(m.pwd,'getpwnam',return_value=SimpleNamespace(pw_gid=group)):
        if case=='valid': assert m._protected_record(path,'SELECTOR')==data
        else:
            with pytest.raises(m.Stop) as caught: m._protected_record(path,'SELECTOR')
            assert caught.value.classification==m.PRECONDITION_FAILED


@pytest.mark.parametrize('case', ['reviewed_blob','merged_blob','one_parent','wrong_second_parent','missing_contract','changed_contract','changed_r34'])
def test_merge_blob_and_governance_failures(graph,case):
    record=copy.deepcopy(graph.record)
    if case=='reviewed_blob':
        # A reviewed branch that differs from the merged implementation.
        record['reader']=graph.merge({m.REL_EXECUTOR:b'reviewed different\n'},base=graph.head,
                                    merge_change={m.REL_EXECUTOR:graph.executor})
    elif case=='merged_blob':
        record['reader']=graph.merge({'new':b'new\n'},base=graph.head,
                                    merge_change={m.REL_EXECUTOR:b'merged different\n'})
    elif case=='one_parent':
        record['reader']['merge_sha']=record['reader']['reviewed_head_sha']
    elif case=='wrong_second_parent':
        record['reader']['reviewed_head_sha']=graph.r32['reviewed_head_sha']
    else:
        graph.git('checkout','--detach',graph.head)
        if case=='missing_contract':
            graph.git('rm',m.REL_TRUST)
        else: graph.write(m.REL_TRUST if case=='changed_contract' else m.REL_R34,b'altered\n')
        record['expected_runtime_head']=graph.commit()
    graph.republish(record, base=record["expected_runtime_head"]); graph.assert_stop()


def test_evidence_not_actual_merge_rejected(graph):
    graph.sel['evidence_commit']=graph.git('show','-s','--format=%P',graph.sel['evidence_commit']).split()[1]
    graph.assert_stop()


def test_predecessor_transport_mismatch(graph):
    first=graph.sel.copy(); record=copy.deepcopy(graph.record)
    record['binding_id']='22345678-1234-1234-1234-123456789abc'
    record['supersedes']=dict(kind='recovery-evidence-v1',commit=first['evidence_commit'],path=first['evidence_path'],transport_sha256='f'*64)
    graph.republish(record,base=first['evidence_commit']); graph.assert_stop()


def test_historical_activation_never_accepted(graph):
    graph.act.update(pr_number=289,reviewed_head_sha='a'*40,authority_merge_sha='b'*40)
    graph.act['schema_version']='aios-stage-0.33c-p4s7-r13-post-merge-activation-v1'
    graph.assert_stop()


def test_protocol_constants_match_merged_contract():
    contract=ROOT/m.REL_TRUST
    assert m.sha256(contract.read_bytes())==m.TRUST_SHA256
    assert m.TRUST_MERGE=='7f124e307d9a516b4ce278d800c92d29d476cf5e'
    assert m.R32_MERGE=='ba717f6990d775748f46d62ef03a696f1618077b'
    assert m.R34_MERGE=='8e9a8023742773b055e17dba002b2ebf07528118'
    assert m.ACTIVATION_RECORD.name=='p4s7-recovery-activation.json'
    assert m.TRUST_SELECTOR.name=='p4s7-recovery-review-merge-trust.json'


def test_authenticated_chain_and_real_package_reach_claim_boundary(tmp_path,monkeypatch):
    """Complete synthetic preclaim flow, stopped before the first mutation.

    The fixture assumes independent operator authorization as an external test
    precondition, not a machine-readable approval token or a claim of live review.
    """
    import stat
    from tests.unit.intelligence import test_stage033c_registry_manifest_matrix as matrix
    f=matrix.fixture(tmp_path/'package')
    payload=f['approval']['package_payload']
    payload.update(approval_id=m.RECOVERY_APPROVAL_ID,approved_at_utc=m.RECOVERY_APPROVED_AT,not_after_utc=m.RECOVERY_NOT_AFTER)
    approval=matrix.rehash(f)
    monkeypatch.setattr(m,'RECOVERY_PAYLOAD_SHA256',f['approval']['package_payload_sha256'])
    monkeypatch.setattr(m,'RECOVERY_TF_A',payload['trusted_facts_sha256'])
    monkeypatch.setattr(m,'utc_now',lambda:m.parse_utc('2026-09-27T01:30:00.000000Z'))
    monkeypatch.setattr(m,'EXPECTED_INTERPRETER',sys.executable)
    monkeypatch.setattr(m,'EXPECTED_PYTHON_VERSION',tuple(sys.version_info[:3]))
    graph=Graph(tmp_path,monkeypatch)
    parent=tmp_path/'runtime'; parent.mkdir(mode=0o750)
    (parent/m.EVIDENCE_DIR).mkdir(mode=0o700)
    sources=[tmp_path/'input',tmp_path/'approval']
    for path in sources: path.mkdir(mode=0o700)
    transports=(f['input_transport'],approval)
    specs=tuple((name,len(data)-1,len(data),m.sha256(data[:-1])) for name,data in zip(
        ('approved-input.json','approved-input-approval.json'),transports))
    for source,spec,data in zip(sources,specs,transports):
        path=source/spec[0]; path.write_bytes(data); path.chmod(0o400)
    monkeypatch.setattr(m,'FILES',specs)
    monkeypatch.setattr(m,'RUNTIME_PARENT',parent)
    monkeypatch.setattr(m,'INPUT_SOURCE_PARENT',sources[0])
    monkeypatch.setattr(m,'APPROVAL_SOURCE_PARENT',sources[1])
    opened=[]
    def open_fixture(path,*args,**kwargs):
        assert path in (parent,*sources)
        opened.append(path)
        return os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    monkeypatch.setattr(m,'open_dir',open_fixture)
    monkeypatch.setattr(m.pwd,'getpwnam',lambda name:SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid()))
    real_fstat=os.fstat
    def owned_file(fd):
        raw=real_fstat(fd)
        if stat.S_ISREG(raw.st_mode):
            fields=list(raw); fields[4]=fields[5]=0; return os.stat_result(fields)
        return raw
    monkeypatch.setattr(m.os,'fstat',owned_file)
    real_validate=m.validate_frozen_package
    monkeypatch.setattr(m,'validate_frozen_package',lambda i,a:real_validate(i,a,manifest_root=f['manifest_root'],retained_root=f['retained']))
    class ClaimBoundaryReached(Exception): pass
    with patch.object(m,'durable_claim',side_effect=ClaimBoundaryReached) as claim, \
         patch.object(m,'read_source',wraps=m.read_source) as reads, \
         patch.object(m,'stage_and_publish') as staging, patch.object(m.os,'link') as publication:
        with pytest.raises(ClaimBoundaryReached): m.main()
        assert claim.call_count==1 and reads.call_count==2
        assert opened==[parent,*sources]
        staging.assert_not_called(); publication.assert_not_called()
    assert not (parent/m.EVIDENCE_DIR/m.MARKER).exists()
    assert sorted(p.name for p in parent.iterdir())==[m.EVIDENCE_DIR]


@pytest.mark.parametrize('timestamp', ['1900-01-01T00:00:00.000000Z', '2026-10-03T23:24:12.093093Z', '2026-09-28T00:00:00.000000Z'])
def test_locally_invalid_activation_time(graph,timestamp):
    graph.act['activated_at_utc']=timestamp
    assert graph.assert_stop().stage=='ACTIVATION_TIME'
