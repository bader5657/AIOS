"""M4 static inventory compiler: symbolic data replay only; no adapter or test runner.
Paths are inert strings. The only write, in main(), is the generated package JSON.
"""
import collections
import copy
import hashlib
from functools import lru_cache
import json
from pathlib import Path
import pathlib
import re

P = Path(__file__).parent

def can(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode()

def digest(value):
    return hashlib.sha256(can(value)).hexdigest()

def calls(primitive,src,dst):
    out=[]
    def add(action,path,role='subject'):out.append({'action':action,'path':path,'role':role})
    # Held descriptors do not eliminate required full ancestor revalidation.
    paths=sorted({str(pathlib.PurePosixPath(x).parent) for x in (src,dst) if x and x.startswith('/')})
    ancestors=sorted({str(a) for x in paths for a in [pathlib.PurePosixPath(x),*pathlib.PurePosixPath(x).parents]},key=lambda x:(x.count('/'),x))
    for a in ancestors:
        add('openat_DIRECTORY_NOFOLLOW',a,'ancestor_before');add('fstat_verify_directory',a,'ancestor_before')
    if primitive in ('create_file','create_directory'):
        add('fstatat_absence_NOFOLLOW',dst,'destination_absence')
        if primitive=='create_file':
            if src:
                for act in ('openat_NOFOLLOW_read','fstat_verify_regular','read_and_hash_verify','fstat_verify_regular'):add(act,src,'approved_input')
            for act in ('openat_O_EXCL_NOFOLLOW','fstat_verify_regular','write_all','fchmod_new_fd','fstat_verify_regular','fsync_file'):add(act,dst)
        else:
            for act in ('mkdirat','openat_DIRECTORY_NOFOLLOW','fstat_verify_directory','fchmod_new_fd','fsync_directory'):add(act,dst)
        add('fsync_parent',str(pathlib.PurePosixPath(dst).parent),'destination_parent')
        if primitive=='create_file':
            for act in ('reopenat_NOFOLLOW','fstat_verify_regular','read_and_hash_verify','fstat_verify_regular'):add(act,dst,'post_fsync_validation')
    elif primitive in ('link','move','exchange'):
        add('fstatat_verify_NOFOLLOW',src,'source')
        add('fstatat_verify_NOFOLLOW' if primitive=='exchange' else 'fstatat_absence_NOFOLLOW',dst,'destination')
        add({'link':'linkat_flags0','move':'renameat2_NOREPLACE','exchange':'renameat2_EXCHANGE'}[primitive],dst,'source='+src)
        add('fsync_moved_inode' if primitive=='move' else 'fsync_file',dst,'published_inode')
        if primitive=='exchange':add('fsync_file',src,'exchanged_inode')
        for parent in sorted({str(pathlib.PurePosixPath(x).parent) for x in (src,dst)}):add('fsync_parent',parent,'affected_parent')
        for path in (src,dst):add('fstatat_absence_NOFOLLOW' if primitive=='move' and path==src else 'fstatat_verify_NOFOLLOW',path,'post_namespace')
        if primitive=='link':
            for path in (src,dst):add('read_and_hash_verify',path,'alias_content')
    elif primitive=='verify_object':
        for act in ('openat_NOFOLLOW_read','fstat_verify_regular','read_and_strict_zlib_decode','verify_object_type_length_sha1_sha256','fstat_verify_regular'):add(act,src or 'release://approved-object-stream','object')
    elif primitive=='verify_graph':
        add('read_graph_without_replace_or_alternates',src,'graph')
        add('verify_all_5426_object_identities',src,'graph')
    elif primitive=='verify_clean':
        for act in ('read_complete_index_tree_worktree','verify_full_status_and_custody','verify_service_and_governance_gates'):add(act,src,'acceptance')
    elif primitive=='verify':
        for act in ('fstatat_verify_NOFOLLOW','read_and_hash_verify'):add(act,src,'control_inventory')
    for a in ancestors:
        add('openat_DIRECTORY_NOFOLLOW',a,'ancestor_after');add('fstat_verify_directory',a,'ancestor_after')
    return out

def modes(action,role):
    result=['PROCESS_CRASH_BEFORE','PROCESS_CRASH_AFTER']
    if action.startswith('fsync'):return result+['EIO','ENOSPC','POWER_LOSS_BEFORE_DURABILITY','POWER_LOSS_AFTER_DURABILITY']
    if action=='write_all':return result+['SHORT_WRITE_THEN_SUCCESS','EINTR_THEN_SUCCESS','PARTIAL_WRITE_THEN_EIO','PARTIAL_WRITE_THEN_ENOSPC','CRASH_DURING_PARTIAL_WRITE']
    if action=='fchmod_new_fd':return result+['EPERM','EIO']
    if action=='mkdirat':return result+['EACCES','EPERM','ENOSPC','EEXIST_FOREIGN_ENTRY']
    if action=='linkat_flags0':return result+['EACCES','EPERM','ENOSPC','EXDEV','EEXIST_FOREIGN_ENTRY','CONCURRENT_NAMESPACE_REPLACEMENT']
    if action.startswith('renameat2'):return result+['EACCES','EPERM','ENOSPC','EXDEV','ENOSYS','EINVAL_UNSUPPORTED_FLAGS','CONCURRENT_NAMESPACE_REPLACEMENT']+(['EEXIST_FOREIGN_DESTINATION'] if action.endswith('NOREPLACE') else ['FOREIGN_EXCHANGE_INODE'])
    if action=='openat_O_EXCL_NOFOLLOW':return result+['EACCES','EPERM','ENOSPC','EEXIST_FOREIGN_ENTRY','SYMLINK_COMPONENT','CONCURRENT_NAMESPACE_REPLACEMENT']
    if action in ('openat_DIRECTORY_NOFOLLOW','openat_NOFOLLOW_read','reopenat_NOFOLLOW'):
        return result+['EACCES','EIO','SYMLINK_COMPONENT','CONCURRENT_NAMESPACE_REPLACEMENT']
    if action=='fstatat_absence_NOFOLLOW':return result+['EACCES','EIO','UNEXPECTED_PRESENT_ENTRY']
    if action.startswith('fstat'):
        return result+['EIO','WRONG_OWNER','WRONG_GROUP','WRONG_MODE','WRONG_TYPE','LINK_COUNT_MISMATCH','CONCURRENT_NAMESPACE_REPLACEMENT']
    if action in ('read_and_strict_zlib_decode','verify_object_type_length_sha1_sha256','verify_all_5426_object_identities'):
        return result+['EIO','EINTR_THEN_SUCCESS','CORRUPTED_OBJECT','WRONG_TYPE','WRONG_LENGTH','WRONG_SHA1','WRONG_SHA256','TRAILING_ZLIB_BYTES']
    if action.startswith('read'):return result+['EIO','SHORT_READ_THEN_SUCCESS','EINTR_THEN_SUCCESS','CONTENT_HASH_MISMATCH']
    if action=='verify_full_status_and_custody':return result+['ANCILLARY_MISSING','AUTH_CUSTODY_CHANGED','HEAD_TARGET_INDEX_INCOMPLETE','INDEX_ONLY','SAME_HASH_FOREIGN_INODE']
    if action=='verify_service_and_governance_gates':return result+['CUSTODY_LOST','REVOKED','SERVICE_IDENTITY_CHANGED']
    if action=='verify_terminal':return ['TERMINAL_INVARIANT_LOSS','TERMINAL_LEDGER_CONTRADICTION','TERMINAL_ALIAS_SPLIT']
    if action=='flock_LOCK_EX_NB':return result+['EWOULDBLOCK','EINTR','EBADF']
    if action=='verify_phase_namespace_and_git':return result+['MISSING_REQUIRED_ALIAS','UNEXPECTED_ALIAS','LINK_COUNT_MISMATCH','SAME_HASH_FOREIGN_INODE','WRONG_OWNER','WRONG_GROUP','WRONG_MODE','WRONG_TYPE','CONTENT_HASH_MISMATCH','PARENT_REPLACEMENT','HEAD_INDEX_WORKTREE_CONTRADICTION','LEDGER_EVIDENCE_CONTRADICTION','CUSTODY_LOST']
    raise ValueError(action)



# Only these exact partial-write witnesses are in this finite prepared inventory.
# Other byte cuts require separately bound additional cases, never a wildcard case.
PREFIX_LENGTHS = (1, 2)
EMPTY = {'sha256': hashlib.sha256(b'').hexdigest(), 'length': 0}
MAP_FIELDS = ('before_identity', 'after_identity', 'parent_before_identity',
              'parent_after_identity', 'content_sha256', 'link_count_changes')
RULES = {
    'STOP_TORN_RECORD': '02 ledger/STOP: retained bytes do not form a complete trusted record; no repair or append',
    'STOP_AMBIGUOUS_EFFECT': '02 pending BEFORE / 04 interruption: unproved effects require governed recovery',
    'STOP_PRESERVE': '02 STOP: durable STOP, revocation or known failure halts; preserve evidence',
    'STOP_RECOVERY_REQUIRED': '04 terminal invariants / unproved initialization: new governed recovery required',
    'TERMINAL_INSPECTION_ONLY': '04 terminal VERIFIED/ROLLED_BACK: inspect only, no mutation',
    'CONTINUE_SAME_CALL': '02 short read/write and EINTR: finish the exact call, then reverify',
    'CONTINUE_PROVED_PREFIX': '02 clean proved prefix: next prescribed record only under separate release',
}


def expand_event(components, reference):
    packed = components[reference]
    payload = dict(packed['scalars'])
    payload.update({key: None if value is None else components[value]
                    for key, value in packed['maps'].items()})
    return payload


def snapshot_observations(components, reference):
    snapshot = components[reference]
    ns, inodes = components[snapshot['namespace']], components[snapshot['inodes']]
    result = {}
    aliases=collections.Counter(t for t in ns.values() if t is not None)
    children=collections.Counter(parent_path(q) for q,t in ns.items() if t is not None and inodes[t]['file_type']=='directory')
    for path, token in ns.items():
        if token is None:
            result[path] = None
            continue
        inode = inodes[token]
        if inode['file_type'] == 'directory':
            count = children[path] - (path=='/' and ns.get('/') is not None)
            content_hash = None
        else:
            count = aliases[token]
            assert 'sha256' in inode['content'], 'unproved partial content cannot become evidence'
            content_hash = inode['content']['sha256']
        result[path] = {k: inode[k] for k in ('dev','ino','uid','gid','mode','file_type')}
        result[path].update(sha256=content_hash, nlink=inode['outside_links']+count)
    return result


class InvalidFilesystem(ValueError):
    pass


class UnboundCoverage(ValueError):
    """Meaningful fault with an unavailable approved concrete witness."""
    def __init__(self, reason, required_binding):
        super().__init__(reason)
        self.required_binding = required_binding


NAMESPACE_ROLES = {
    'CONTENT_HASH_MISMATCH':'regular_content',
    'UNEXPECTED_ALIAS':'regular_hardlink_source',
    'LINK_COUNT_MISMATCH':'regular_hardlink_source',
    'WRONG_OWNER':'regular_metadata', 'WRONG_GROUP':'regular_metadata',
    'WRONG_MODE':'regular_metadata',
    'WRONG_TYPE':'regular_symlink_replacement',
    'SAME_HASH_FOREIGN_INODE':'regular_replacement',
    'CONCURRENT_NAMESPACE_REPLACEMENT':'regular_replacement',
    'PARENT_REPLACEMENT':'directory_replacement',
}


CONTROL_FAULTS = {'CUSTODY_LOST','REVOKED','SERVICE_IDENTITY_CHANGED','AUTH_CUSTODY_CHANGED'}
TARGET_ROLES = {
    **NAMESPACE_ROLES,
    'WRONG_OWNER':'metadata_object', 'WRONG_GROUP':'metadata_object',
    'WRONG_MODE':'metadata_object', 'LINK_COUNT_MISMATCH':'link_count_object',
    'WRONG_TYPE':'symlink_replaceable_path', 'SYMLINK_COMPONENT':'symlink_replaceable_path',
    'CONCURRENT_NAMESPACE_REPLACEMENT':'replaceable_path',
    'EEXIST_FOREIGN_ENTRY':'exclusive_creation_path',
    'UNEXPECTED_PRESENT_ENTRY':'exclusive_creation_path',
    'EEXIST_FOREIGN_DESTINATION':'exclusive_creation_path',
    'FOREIGN_EXCHANGE_INODE':'replaceable_path',
    'CORRUPTED_OBJECT':'git_object_content',
    'HEAD_INDEX_WORKTREE_CONTRADICTION':'regular_content',
    'TERMINAL_INVARIANT_LOSS':'regular_content',
    'TERMINAL_ALIAS_SPLIT':'regular_replacement',
    'LEDGER_EVIDENCE_CONTRADICTION':'ledger_file_creation',
    'TERMINAL_LEDGER_CONTRADICTION':'ledger_file_creation',
    'ANCILLARY_MISSING':'regular_removal', 'MISSING_REQUIRED_ALIAS':'regular_removal',
    'PARTIAL_WRITE_THEN_EIO':'regular_content',
    'PARTIAL_WRITE_THEN_ENOSPC':'regular_content',
    'CRASH_DURING_PARTIAL_WRITE':'regular_content',
}


def whole_namespace_call(call):
    return (call['role']=='full_controlled_namespace_plus_protected_custody'
            or call['action'] in ('read_complete_index_tree_worktree',
                                 'verify_full_status_and_custody','verify_terminal'))


def bound_fault_precheck(call, failure, ns, ins):
    """Physical constraints precede missing bytes/path bindings. No proof is made.
    fstat acts on the held inode, not on a replacement pathname or Git header.
    A release-stream descriptor has a regular-file contract even before its
    approved concrete binding is supplied; changing that inode's type is impossible.
    """
    inode=ins.get(ns.get(call['path']))
    held=call['action'].startswith('fstat_')
    kind=inode['file_type'] if inode else ('regular' if call['action']=='fstat_verify_regular'
                                        else 'directory' if call['action']=='fstat_verify_directory' else None)
    if held and failure=='WRONG_TYPE':
        raise InvalidFilesystem('held descriptor inode cannot change file type')
    if call['role']=='object' and inode is not None and failure in (
            'CORRUPTED_OBJECT','WRONG_TYPE','WRONG_LENGTH','WRONG_SHA1','WRONG_SHA256','TRAILING_ZLIB_BYTES'):
        fs_require(kind=='regular','object bytes require a regular content-bearing file')
    return {'held_descriptor':held,'bound_object_type':kind,
            'type_basis':'concrete_inode' if inode else 'descriptor_contract' if kind else 'unbound'}


def require_target_capability(ns, ins, path, role):
    fs_require(isinstance(path,str) and canonical_path(path),'concrete target is not a canonical path')
    inode=ins.get(ns.get(path));kind=inode['file_type'] if inode else None
    regular={'regular_content','git_object_content','regular_hardlink_source',
             'regular_metadata','regular_replacement','regular_symlink_replacement','regular_removal'}
    if role in regular:fs_require(kind=='regular','target role requires an existing regular file')
    elif role=='directory_replacement':fs_require(kind=='directory','target role requires an existing directory')
    elif role in ('metadata_object','link_count_object'):
        fs_require(kind in ('regular','directory'),'target role requires a metadata/link-capable object')
    elif role in ('exclusive_creation_path','ledger_file_creation'):
        fs_require(inode is None,'target role requires an absent creation path')
    elif role not in ('replaceable_path','symlink_replaceable_path'):
        raise ValueError('INVALID_COMPILER_CASE: unknown target role '+role)
    if role in ('regular_content','git_object_content'):
        fs_require(isinstance(inode['content'],dict) and 'sha256' in inode['content'],
                   'content witness lacks bound regular bytes')
    if role not in ('metadata_object','link_count_object','regular_metadata'):
        fs_require(path!='/','traversal root cannot be replaced')
        parent=ins.get(ns.get(parent_path(path)))
        fs_require(parent is not None and parent['file_type']=='directory','target lacks a traversable parent')


def concrete_witness(call, failure, path, ns, ins):
    role=(NAMESPACE_ROLES[failure] if whole_namespace_call(call) and failure in NAMESPACE_ROLES
          else TARGET_ROLES[failure])
    require_target_capability(ns,ins,path,role)
    return {'namespace_scope_anchor':call['path'] if whole_namespace_call(call) else None,
            'concrete_fault_target':path,'predicate':failure,'witness_role':role}


def namespace_witness(program, ns, ins, failure, call):
    """Scope is a predicate input, never an implied mutation target.
    Only live approved descendants are eligible; injected aliases are not inputs.
    """
    assert whole_namespace_call(call), 'namespace witness requires a namespace predicate'
    if failure not in NAMESPACE_ROLES:
        raise UnboundCoverage('Namespace fault requires an explicit subject binding',
                              {'namespace_scope_anchor':call['path'],'predicate':failure})
    scope=call['path'];role=NAMESPACE_ROLES[failure]
    kind='directory' if role=='directory_replacement' else 'regular'
    approved=program['phase_barriers']['initial_namespace']
    eligible=sorted(q for q,t in ns.items() if q in approved and t is not None
                    and q.startswith(scope.rstrip('/')+'/') and ins[t]['file_type']==kind)
    if not eligible:
        raise UnboundCoverage('No approved concrete descendant satisfies namespace witness role',
                              {'namespace_scope_anchor':scope,'witness_role':role,'required_type':kind})
    return concrete_witness(call,failure,eligible[0],ns,ins)


def external_baseline_snapshot(components, reference, bindings, program_sha256, attempt_root):
    """Bindings are separately authenticated input, never inferred by this compiler.
    No binding is supplied by the prepared inventory. A future adapter must verify
    the surviving evidence and governing approval before supplying this allowlist.
    These records convey baseline proof only, never execution authority.
    """
    if reference is None:return None
    assert reference in bindings, 'external baseline witness is not governed/bound'
    w=components[reference]
    assert set(w)=={'format','snapshot','evidence_sha256','governance_sha256','program_sha256','attempt_root','surviving_durable','approved_scope'}
    assert digest(w)==reference and bindings[reference]==w, 'external witness binding mismatch'
    assert w['format']=='aios-governed-external-baseline-v1'
    assert w['program_sha256']==program_sha256 and w['attempt_root']==attempt_root
    assert w['surviving_durable'] is True and w['approved_scope']=='INITIALIZATION_BASELINE_PROOF_ONLY'
    assert all(isinstance(w[k],str) and re.fullmatch('[0-9a-f]{64}',w[k]) for k in ('snapshot','evidence_sha256','governance_sha256'))
    assert w['snapshot'] in components
    evidence=components[w['evidence_sha256']];governance=components[w['governance_sha256']]
    assert digest(evidence)==w['evidence_sha256'] and digest(governance)==w['governance_sha256']
    assert evidence=={'format':'aios-external-baseline-evidence-v1','snapshot':w['snapshot'],
                      'program_sha256':program_sha256,'attempt_root':attempt_root}
    assert governance=={'format':'aios-external-baseline-approval-v1','evidence_sha256':w['evidence_sha256'],
                        'program_sha256':program_sha256,'attempt_root':attempt_root,
                        'approved_scope':'INITIALIZATION_BASELINE_PROOF_ONLY'}
    return w['snapshot']


def fs_require(condition, reason):
    if not condition:raise InvalidFilesystem(reason)


def ledger_file(path, content):
    identity=digest({'ledger_inode':path})
    return {'path':path,'inode_identity':identity,'dev':2049,
            'ino':10000000000+int(identity[:12],16),'uid':1000,'gid':1000,
            'mode':0o600,'file_type':'regular','nlink':1,'content':{'sha256':content}}


FILE_FIELDS=('path','inode_identity','dev','ino','uid','gid','mode','file_type','nlink')


def file_signature(value):
    assert set(value)==set(FILE_FIELDS)|{'content'}
    content=value['content']
    return tuple(value[k] for k in FILE_FIELDS)+(None if content is None else tuple(sorted(content.items())),)


@lru_cache(maxsize=65536)
def file_digest(signature):
    value=dict(zip(FILE_FIELDS,signature[:-1]))
    value['content']=None if signature[-1] is None else dict(signature[-1])
    return digest(value)


def pack_files(files, intern):
    leaves=[file_digest(file_signature(files[path])) if intern is digest else intern(files[path]) for path in sorted(files)]
    return intern({'file_blocks':[intern(leaves[i:i+32]) for i in range(0,len(leaves),32)],'size':len(leaves)})


def files_at(components, root):
    packed=components[root]
    assert set(packed)=={'file_blocks','size'} and type(packed['size']) is int
    assert all(len(components[b])==(32 if i<len(packed['file_blocks'])-1 else (packed['size']-1)%32+1) for i,b in enumerate(packed['file_blocks']))
    leaves=[h for block in packed['file_blocks'] for h in components[block]]
    assert len(leaves)==packed['size']
    files=[components[h] for h in leaves]
    assert [f['path'] for f in files]==sorted({f['path'] for f in files})
    return {f['path']:f for f in files}


def filesystem_view(components, snapshot, files):
    s=components[snapshot];ns=dict(components[s['namespace']]);ins=dict(components[s['inodes']])
    for path,f in files.items():
        token='LEDGER:'+f['inode_identity'];ns[path]=token
        value={k:f[k] for k in ('dev','ino','uid','gid','mode','file_type','content')}
        value['outside_links']=2 if f['file_type']=='directory' else 0
        if token in ins:fs_require(ins[token]==value,'inconsistent ledger hardlink metadata')
        ins[token]=value
    return ns,ins


@lru_cache(maxsize=65536)
def parent_path(path):
    # All syscall paths are validated as canonical absolute paths before use.
    return path.rsplit('/',1)[0] or '/'


@lru_cache(maxsize=65536)
def canonical_path(path):
    return isinstance(path,str) and (path=='/' or path.startswith('/') and all(x not in ('','.','..') for x in path.split('/')[1:]))


def validate_filesystem(ns, ins):
    fs_require(ns.get('/') in ins and ins[ns['/']]['file_type']=='directory','traversal root must remain a directory')
    groups=collections.defaultdict(list)
    for path,token in ns.items():
        fs_require(canonical_path(path),'noncanonical namespace path')
        if token is None:continue
        fs_require(token in ins,'namespace has no inode')
        if path!='/':
            parent=parent_path(path)
            fs_require(ns.get(parent) in ins and ins[ns[parent]]['file_type']=='directory','present child lacks traversable directory parent')
        groups[token].append(path)
    identity={}
    for token,paths in groups.items():
        inode=ins[token];pair=inode['dev'],inode['ino']
        fs_require(pair not in identity or identity[pair]==token,'inode identity split into distinct tokens')
        identity[pair]=token
        if inode['file_type']=='directory':
            fs_require(len(paths)==1,'directory hardlink is impossible')
            fs_require(inode['outside_links']==2,'directory link count requires actual child-directory entries')
        else:
            fs_require(inode['outside_links']==0,'unbound outside hardlink')
            if inode['file_type']=='symlink':fs_require(inode['mode']==0o777,'Linux symlink mode must be 0777')
    return True


def replay_fault_operations(ns, ins, operations, mount_points=()):
    """Independent filesystem transition validator; operations are fault-actor calls,
    never normal-operation authorization. No Compiler method is called here.
    """
    ns=dict(ns);ins=dict(ins);original_keys=set(ns)
    validate_filesystem(ns,ins)
    anchors={'/',*mount_points}
    anchors.update(q for q,t in ns.items() if t is not None and q!='/'
                   and ins[t]['dev']!=ins[ns[parent_path(q)]]['dev'])
    fs_require(all(q in ns and ns[q] is not None for q in anchors),'unbound mount anchor')
    for op in operations:
        action=op['syscall'];path=op['path']
        fs_require(canonical_path(path),'noncanonical syscall path or traversal anchor alias')
        parent=parent_path(path)
        fs_require(path not in anchors or action in ('fchmod','fchown','ftruncate_write'),'traversal root or mount anchor cannot be replaced')
        fs_require(path=='/' or ns.get(parent) in ins and ins[ns[parent]]['file_type']=='directory','fault path has no traversable parent')
        token=ns.get(path);exists=token is not None
        children=lambda q:any(t is not None and k.startswith(q.rstrip('/')+'/') for k,t in ns.items() if k!=q)
        if action in ('fchmod','fchown','ftruncate_write'):
            fs_require(exists,'metadata/content fault target absent')
            inode=dict(ins[token]);ins[token]=inode
            fs_require(inode['file_type']!='symlink','held-descriptor metadata operation cannot act on a symlink')
            if action=='fchmod':inode['mode']=op['mode']
            elif action=='fchown':inode['uid'],inode['gid']=op['uid'],op['gid']
            else:
                fs_require(inode['file_type']=='regular','write target is not regular')
                inode['content']={'sha256':op['sha256']}
        elif action in ('create_file','mkdirat','symlinkat'):
            fs_require(not exists,'exclusive injected creation target exists')
            inode=copy.deepcopy(op['inode']);new=op['token']
            fs_require(new not in ins,'injected inode is not new')
            fs_require(inode['dev']==ins[ns[parent]]['dev'],'injected creation crosses device boundary')
            fs_require(inode['file_type']=={'create_file':'regular','mkdirat':'directory','symlinkat':'symlink'}[action],'injected creation type mismatch')
            ins[new]=inode;ns[path]=new
        elif action=='linkat':
            source=op['source'];fs_require(canonical_path(source),'noncanonical link source');src=ns.get(source)
            fs_require(src in ins,'hardlink source must exist')
            fs_require(ins[src]['file_type']!='directory','hardlink to directory is prohibited')
            if ins[src]['file_type']!='regular':
                raise UnboundCoverage('Hardlink source type lacks a bound fault replay contract',{'witness_role':'nonregular_hardlink_source','source':source,'path':path})
            fs_require(not exists,'exclusive hardlink destination exists')
            fs_require(ins[src]['dev']==ins[ns[parent]]['dev'],'hardlink crosses device boundary')
            ns[path]=src
        elif action in ('unlinkat','rmdir'):
            fs_require(exists,'removal target absent')
            fs_require((ins[token]['file_type']=='directory')==(action=='rmdir'),'file/directory removal mismatch')
            fs_require(action!='rmdir' or not children(path),'rmdir target is nonempty')
            ns[path]=None
        elif action in ('renameat2_REPLACE','renameat2_NOREPLACE','renameat2_EXCHANGE'):
            source=op['source'];fs_require(canonical_path(source),'noncanonical rename source')
            src=ns.get(source);sp=parent_path(source)
            fs_require(source not in anchors and src in ins,'rename source/root/mount invalid')
            fs_require(not any(q.startswith(source.rstrip('/')+'/') for q in anchors),'rename contains mounted subtree')
            fs_require(ns.get(sp) in ins and ins[ns[sp]]['file_type']=='directory','rename source parent invalid')
            fs_require(ins[ns[sp]]['dev']==ins[ns[parent]]['dev']==ins[src]['dev'],'rename crosses mount/device boundary')
            fs_require(not path.startswith(source.rstrip('/')+'/'),'directory moved into itself')
            fs_require(not exists or ins[token]['dev']==ins[ns[parent]]['dev'],'rename replaces mount boundary')
            # POSIX replacement of another name for this same inode is a no-op.
            if action=='renameat2_REPLACE' and src==token:continue
            if action=='renameat2_NOREPLACE':fs_require(not exists,'NOREPLACE destination exists')
            if action=='renameat2_EXCHANGE':
                fs_require(exists,'exchange endpoint absent')
                fs_require(ins[token]['dev']==ins[src]['dev'],'exchange crosses device boundary')
                # This normative program exchanges regular metadata only. Fault
                # scripts in this finite inventory do not exchange directory trees.
                if not ins[token]['file_type']==ins[src]['file_type']=='regular':
                    raise UnboundCoverage('Exchange endpoint types lack a bound fault replay contract',
                                          {'witness_role':'exchange_endpoints','source':source,'path':path})
                ns[source],ns[path]=token,src
            else:
                if exists:
                    fs_require((ins[token]['file_type']=='directory')==(ins[src]['file_type']=='directory'),'rename file/directory replacement mismatch')
                    fs_require(ins[token]['file_type']!='directory' or not children(path),'replacement directory is nonempty')
                if ins[src]['file_type']=='directory':
                    descendants=[(q,t) for q,t in ns.items() if t is not None and q.startswith(source.rstrip('/')+'/')]
                    fs_require(all(ins[t]['dev']==ins[src]['dev'] for q,t in descendants),'directory rename crosses mounted subtree')
                    for q,t in descendants:ns[q]=None
                    for q,t in descendants:ns[path+q[len(source):]]=t
                ns[source]=None;ns[path]=src
        else:raise ValueError('INVALID_COMPILER_CASE: unsupported injected syscall: '+action)
        # Deleted inode metadata has no surviving identity; inode reuse is never
        # assumed. Retain absent names only from the declared controlled namespace.
        ns={q:t for q,t in ns.items() if t is not None or q in original_keys}
        active=set(ns.values())-{None};ins={t:v for t,v in ins.items() if t in active}
        validate_filesystem(ns,ins)
    return ns,ins


def split_filesystem(ns, ins, declared, ledger_root):
    files={};normal={q:t for q,t in ns.items() if not q.startswith(ledger_root+'/')}
    normal.update({q:normal.get(q) for q in declared if not q.startswith(ledger_root+'/')})
    counts=collections.Counter(t for t in ns.values() if t is not None)
    for path,token in ns.items():
        if not path.startswith(ledger_root+'/') or token is None:continue
        inode=ins[token]
        files[path]={'path':path,'inode_identity':token.removeprefix('LEDGER:'),
                     **{k:inode[k] for k in ('dev','ino','uid','gid','mode','file_type','content')},'nlink':(2+sum(1 for q,t in ns.items() if t and parent_path(q)==path and ins[t]['file_type']=='directory') if inode['file_type']=='directory' else counts[token])}
    active=set(normal.values())-{None}
    return normal,{t:ins[t] for t in active},files


def derive_durable_proof(components, file_root, catalog, external_base, intern, prefix_cache):
    """Scan exact surviving files; fsync-return/bookkeeping is never an input.
    Cache only fully validated immutable 32-file blocks, bound to their incoming
    proof root and snapshot. A changed file changes its block hash and is rescanned.
    """
    root=None;proved=external_base;terminal=None;ordinal=1;prior_hash=None;rejection=None
    for block in components[file_root]['file_blocks']:
        key=(root,proved,block)
        if terminal is not None:rejection='FILE_AFTER_TERMINAL';break
        if key in prefix_cache:
            root,proved,terminal,ordinal,prior_hash=prefix_cache[key]
            continue
        for leaf in components[block]:
            f=components[leaf];path=f['path'];sha=(f['content'] or {}).get('sha256')
            record=catalog.get(sha)
            if terminal is not None:rejection='FILE_AFTER_TERMINAL';break
            if f['file_type']!='regular' or (f['uid'],f['gid'],f['mode'],f['nlink'])!=(1000,1000,0o600,1) or f['inode_identity']!=digest({'ledger_inode':path}) or f['dev']!=2049 or f['ino']!=ledger_file(path,sha)['ino']:
                rejection='UNTRUSTED_FILE_METADATA';break
            if record is None:rejection='PARTIAL_OR_MALFORMED_BYTES';break
            e=expand_event(components,record['payload'])
            if Path(path).name!=f"{ordinal:06d}-{e['operation_id']}-{e['event']}.json" or e['ordinal']!=ordinal or e['previous_event_sha256']!=prior_hash:
                rejection='FILENAME_OR_CHAIN_MISMATCH';break
            # The first accepted, surviving record supplies its authenticated
            # before snapshot. No file, partial bytes or writer phase can do so.
            if ordinal==1 and proved is None:proved=record['before_snapshot']
            if record['before_snapshot']!=proved:rejection='PROOF_CONTINUITY_MISMATCH';break
            root=intern({'previous':root,**record,'file':f})
            proved=record['before_snapshot'] if e['event']=='STOP' else record['after_snapshot']
            if e['event']=='STOP':terminal='STOP'
            elif e['operation_id']=='FINAL' and e['state'] in ('VERIFIED','ROLLED_BACK'):terminal=e['state']
            prior_hash=sha;ordinal+=1
        if rejection:break
        prefix_cache[key]=(root,proved,terminal,ordinal,prior_hash)
    base=external_base
    if ordinal>1 and base is None:
        first=components[components[components[file_root]['file_blocks'][0]][0]]
        base=catalog[first['content']['sha256']]['before_snapshot']
    proof={'base_snapshot':base,'source':'LEDGER' if ordinal>1 else 'EXTERNAL_BASELINE' if external_base is not None else 'NONE',
           'accepted_record_count':ordinal-1,'rejection':rejection}
    return root,proved,terminal,proof


class Compiler:
    """Data-only concrete outcome compiler. No runtime paths are opened."""
    def __init__(self, program):
        self.p = program
        self.root = program['rollback_protocol']['attempt_root']
        self.components, self.states, self.cases = {}, {}, {}
        self.identity_leaf_cache = {}
        self.file_leaf_cache = {}
        self.byte_blobs = {}
        self.prefix_bytes = {}
        self.corruption_cache = {}
        self.canonical_cache = {}
        self.file_map_cache = {None:{}}
        self.file_frame_cache = {}
        self.proof_cache = {}
        self.proof_prefix_cache = {}
        self.records = {}
        # Empty unless separately governed evidence is explicitly supplied.
        self.external_baseline_witness = None
        self.external_baseline_bindings = {}
        self.origins, self.fixtures, self.invalid = [], [], []
        self.normal_prefixes = {}
        self.action_counts = collections.Counter()
        self.raw = 0
        self.history = {}
        self.rollback_primitives = set()
        self.ns = dict(program['phase_barriers']['initial_namespace'])
        self.inodes = {}
        self.steps = {s['id']:s for o in program['operations'] for s in o['microsteps']}
        self.steps.update({s['id']:s for s in program['rollback_occurrences']})
        self.ops = {o['operation_id']:o for o in program['operations']}
        tokens = sorted((set(self.ns.values())-{None}) | set(program['created_identity_contracts']))
        start = max(x['ino'] or 0 for x in program['baseline_identity_constraints'].values())+1000
        self.ino = {token:start+i for i,token in enumerate(tokens)}
        self.full_content = {}
        for path,token in self.ns.items():
            if token is None or token in self.inodes:
                continue
            pin = program['baseline_identity_constraints'].get(path, {})
            inode = {'dev':2049,'ino':self.ino[token],'uid':1000,'gid':1000,
                     'mode':0o755,'file_type':'directory' if token.startswith('BASE:') else 'regular','outside_links':2,'content':None}
            inode.update({k:v for k,v in pin.items() if v is not None and k!='sha256'})
            if inode['file_type'] == 'regular':
                inode['outside_links'] = 0
                inode['content'] = {'sha256':pin.get('sha256') or digest({'synthetic_fixture_content':token})}
            self.inodes[token] = inode
        for token,contract in program['created_identity_contracts'].items():
            if contract['file_type'] == 'regular':
                self.full_content[token] = {'sha256':contract['sha256'] or digest({'synthetic_fixture_content':token})}
        for step in self.steps.values():
            if step['primitive']=='create_file' and step['source'] is not None:
                self.full_content[step['created_token']] = dict(self.inodes[self.ns[step['source']]]['content'])
        self.ledger = self.proved = self.pending = self.terminal = self.last_event = None
        self.ledger_count = 0
        self.controls = {'release_revoked':False}
        self.cursor = None
        self.program_hash = digest(program)
        self.bound_inputs = self.intern({'initial_namespace':self.ns,'initial_inodes':self.inodes,
                                        'full_content':self.full_content,'created_inode_numbers':self.ino,
                                        'external_baseline_bindings':self.external_baseline_bindings})
        self.audit = OutcomeAudit(program, self.components, self.bound_inputs)
        self.audit.catalog = self.records

    def intern(self, value):
        file_key=None
        if isinstance(value,dict) and 'inode_identity' in value:
            file_key=file_signature(value)
            if file_key in self.file_leaf_cache:return self.file_leaf_cache[file_key]
        key = digest(value)
        if key in self.components:
            assert self.components[key] == value, 'SHA256 collision / noncanonical component'
        else:
            if isinstance(value,dict) and value and all(isinstance(v,dict) and {'dev','ino','mode'}<=set(v) for v in value.values()):
                shared={}
                for name,leaf in value.items():
                    h=tuple((k,tuple(sorted(v.items())) if isinstance(v,dict) else v) for k,v in sorted(leaf.items()))
                    if h not in self.identity_leaf_cache:self.identity_leaf_cache[h]=copy.deepcopy(leaf)
                    else:assert self.identity_leaf_cache[h]==leaf,'identity leaf hash collision'
                    shared[name]=self.identity_leaf_cache[h]
                self.components[key]=shared
            else:self.components[key] = copy.deepcopy(value)
        if file_key is not None:self.file_leaf_cache[file_key]=key
        return key

    def normalized_content(self, value):
        if value is None:return None
        if 'bytes_hex' in value:
            data=bytes.fromhex(value['bytes_hex'])
            assert hashlib.sha256(data).hexdigest()==value['sha256']
            self.byte_blobs[value['sha256']]=value['bytes_hex']
        return {'sha256':value['sha256']} if 'sha256' in value else value

    def snapshot(self):
        active = set(self.ns.values())-{None}
        return self.intern({'namespace':self.intern(self.ns),
                            'inodes':self.intern({t:{**self.inodes[t],'content':self.normalized_content(self.inodes[t]['content'])} for t in active})})

    def save(self):
        return copy.deepcopy((self.ns,self.inodes,self.ledger,self.proved,self.pending,
                              self.terminal,self.last_event,self.ledger_count,self.controls))

    def restore(self, value):
        (self.ns,self.inodes,self.ledger,self.proved,self.pending,self.terminal,
         self.last_event,self.ledger_count,self.controls) = copy.deepcopy(value)

    def frame(self):
        actual = self.snapshot()
        return {'ledger_root':self.ledger,'last_proved_snapshot':self.proved,
                'actual_snapshot':actual,'pending_ledger_file':copy.deepcopy(self.pending),
                'persistent_controls':dict(self.controls),'terminal':self.terminal}

    def physical_files(self, frame):
        if 'ledger_files_override' in frame:return files_at(self.components,frame['ledger_files_override'])
        root=frame['ledger_root'];missing=[];cursor=root
        while cursor not in self.file_map_cache:
            missing.append(cursor);cursor=self.components[cursor]['previous']
        for key in reversed(missing):
            node=self.components[key];files=dict(self.file_map_cache[node['previous']])
            f=copy.deepcopy(node['file']);f['content']=self.normalized_content(f['content']);files[f['path']]=f
            self.file_map_cache[key]=files
        files=self.file_map_cache[root]
        if frame['pending_ledger_file'] is not None:
            files=dict(files);f=copy.deepcopy(frame['pending_ledger_file']);f['content']=self.normalized_content(f['content']);files[f['path']]=f
        return files

    def canonical_frame(self, frame):
        external=frame.get('external_baseline_witness',self.external_baseline_witness)
        base=external_baseline_snapshot(self.components,external,self.external_baseline_bindings,self.program_hash,self.root)
        source=frame['ledger_files_override'] if 'ledger_files_override' in frame else (frame['ledger_root'],digest(frame['pending_ledger_file']))
        if source not in self.file_frame_cache:
            self.file_frame_cache[source]=frame['ledger_files_override'] if 'ledger_files_override' in frame else pack_files(self.physical_files(frame),self.intern)
        file_root=self.file_frame_cache[source];pk=(file_root,base)
        if pk not in self.proof_cache:
            self.proof_cache[pk]=derive_durable_proof(self.components,file_root,self.records,base,self.intern,self.proof_prefix_cache)
        root,proved,terminal,proof=self.proof_cache[pk]
        return {'ledger_root':root,'last_proved_snapshot':proved,'external_baseline_witness':external,
                'actual_snapshot':frame['actual_snapshot'],'ledger_files':file_root,
                'durable_proof_state':dict(proof),'persistent_controls':dict(frame['persistent_controls']),'terminal':terminal}

    def finish_state(self, frame, disposition):
        state=self.canonical_frame(frame)
        delta=state['actual_snapshot']!=state['last_proved_snapshot']
        rejection=state['durable_proof_state']['rejection']
        if rejection:
            uncertainty='UNTRUSTED_LEDGER'
            recovery='STOP_TORN_RECORD' if rejection=='PARTIAL_OR_MALFORMED_BYTES' else 'STOP_RECOVERY_REQUIRED'
        elif disposition=='SAME_CALL' and not any(state['persistent_controls'].values()) and state['terminal'] is None:
            uncertainty,recovery='LIVE_CALL_CONTINUATION','CONTINUE_SAME_CALL'
        elif state['terminal']=='STOP' or any(state['persistent_controls'].values()):
            uncertainty='UNPROVED_EFFECT' if delta else 'NONE'
            recovery='STOP_AMBIGUOUS_EFFECT' if delta else 'STOP_PRESERVE'
        elif state['last_proved_snapshot'] is None or state['terminal'] and delta:
            uncertainty,recovery='RECOVERY_AUTHORITY_REQUIRED','STOP_RECOVERY_REQUIRED'
        elif delta:uncertainty,recovery='UNPROVED_EFFECT','STOP_AMBIGUOUS_EFFECT'
        elif disposition=='FAILURE':uncertainty,recovery='KNOWN_FAILURE','STOP_PRESERVE'
        elif state['terminal']:uncertainty,recovery='NONE','TERMINAL_INSPECTION_ONLY'
        else:uncertainty,recovery='NONE','CONTINUE_PROVED_PREFIX'
        snap=self.components[state['actual_snapshot']];ns=self.components[snap['namespace']]
        state.update(format='aios-persistent-state-v7',uncertainty_class=uncertainty,required_recovery_action=recovery,
            observed_or_possible_unproved_effects=None if not delta else {'classification':'UNKNOWN_TO_EVIDENCE','actual_snapshot':state['actual_snapshot']},
            git={'HEAD':ns.get('/opt/aios-src/.git/HEAD'),'index':ns.get('/opt/aios-src/.git/index'),
                 'worktree_namespace':snap['namespace'],'content_identities':snap['inodes']})
        return state

    def event(self, oid, kind, mid, state, plan=None):
        if self.proved is None:
            self.proved = self.snapshot()
        before_root = self.proved
        after_root = None if kind=='STOP' else self.snapshot()
        if kind not in ('AFTER','STOP'):
            assert before_root == after_root, ('unproved state at event',oid,kind,mid)
        before = snapshot_observations(self.components,before_root)
        after = None if after_root is None else snapshot_observations(self.components,after_root)
        before_ns = self.components[self.components[before_root]['namespace']]
        after_ns = before_ns if after_root is None else self.components[self.components[after_root]['namespace']]
        before_counts = {token:before[path]['nlink'] for path,token in before_ns.items() if token}
        after_counts = {} if after is None else {token:after[path]['nlink'] for path,token in after_ns.items() if token}
        content_map = {token:(before if after is None else after)[path]['sha256']
                       for path,token in after_ns.items() if token and
                       (before if after is None else after)[path]['file_type']=='regular'}
        label = {'INTENT':'OPERATION_INTENT','BEFORE':'MICROSTEP_BEFORE','AFTER':'MICROSTEP_AFTER',
                 'STAGED':'STAGED_IDENTITY','STOP':'STOP'}.get(kind)
        if kind=='DONE':
            label = 'STATE_SEAL' if oid=='FINAL' else 'ROLLBACK_BARRIER' if mid.startswith('BARRIER:') else 'ROLLBACK_PRIMITIVE_COMPLETE' if oid=='ROLLBACK' else 'OPERATION_COMPLETE'
        git = None
        if oid=='FINAL' and state in self.p['states']:
            git = self.p['phase_barriers']['forward'][state]['git_predicate']
        elif oid=='VERIFY' and kind in ('AFTER','DONE'):
            git = self.p['phase_barriers']['forward']['VERIFIED']['git_predicate']
        elif mid.startswith('BARRIER:') or state=='ROLLED_BACK':
            git = {'head_identity':after_ns['/opt/aios-src/.git/HEAD'],
                   'index_identity':after_ns['/opt/aios-src/.git/index'],
                   'ancillary_present':[o for o in ('F001','F002','F003') if after_ns[self.ops[o]['rule']['path']] is not None],
                   'protected_worktree':'UNCHANGED_PR306_OVERLAY',
                   'status_class':'EXACT_ORIGINAL_TWO_ENTRY_DIRTY' if mid in ('BARRIER:PRE_ROLLBACK_SEAL','SEAL:ROLLED_BACK') else 'EXACT_REPLAYED_TRANSITIONAL_STATUS'}
        step = self.steps.get(mid) if kind in ('BEFORE','AFTER','STAGED') or oid=='ROLLBACK' and kind=='DONE' else None
        op = self.ops.get(oid)
        event = {'attempt_root':self.root,'ordinal':self.ledger_count+1,
                 'previous_event_sha256':None if self.ledger is None else self.components[self.ledger]['event_sha256'],
                 'operation_id':oid,'event':kind,'actual_utc':'2026-09-30T00:00:00.000000Z',
                 'source_path':step['source'] if step else None,'destination_path':step['destination'] if step else None,
                 'before_identity':before,'after_identity':after,
                 'parent_before_identity':{q:i for q,i in before.items() if i and i['file_type']=='directory'},
                 'parent_after_identity':None if after is None else {q:i for q,i in after.items() if i and i['file_type']=='directory'},
                 'content_sha256':content_map,
                 'expected_git_oid_if_object':{k:op['rule'][k] for k in ('oid','object_type','raw_bytes','raw_sha256')} if op and op['kind']=='object' else None,
                 'link_count_changes':None if kind=='STOP' else {t:{'before':before_counts.get(t,0),'after':after_counts.get(t,0)} for t in before_counts.keys()|after_counts.keys() if before_counts.get(t,0)!=after_counts.get(t,0)},
                 'state':state,
                 'durability_checks':{'microstep_id':mid,'program_sha256':self.program_hash,'verified':True,'durable':True,
                     'evidence':{'kind':label,'git_facts':git,'checks':[] if kind=='STOP' else [label,mid,state],
                                 'stop_reason':'REVOKED' if kind=='STOP' else None,'outcome':'UNKNOWN_RETAIN' if kind=='STOP' else 'PROVEN'}}}
        packed = {'scalars':{k:v for k,v in event.items() if k not in MAP_FIELDS},
                  'maps':{k:None if event[k] is None else self.intern(event[k]) for k in MAP_FIELDS}}
        data=can(event);event_hash=hashlib.sha256(data).hexdigest()
        self.prefix_bytes[event_hash]={n:data[:n] for n in PREFIX_LENGTHS}
        record={'payload':self.intern(packed),'event_sha256':event_hash,'before_snapshot':before_root,
                'after_snapshot':after_root,'rollback_plan':plan,'bytes_length':len(data)}
        self.records[event_hash]=record
        return record

    def apply(self, call, step=None, record=None):
        action,path = call['action'],call['path']
        if record is not None:
            if action=='openat_O_EXCL_NOFOLLOW':
                assert self.pending is None
                self.pending = ledger_file(path,EMPTY['sha256'])
            elif action=='write_all':
                self.pending['content'] = {'sha256':record['event_sha256'],'length':record['bytes_length']}
            elif action=='fchmod_new_fd':
                self.pending['mode'] = 0o600
            elif action=='fsync_parent':
                assert self.pending['content']['sha256']==record['event_sha256']
                event = expand_event(self.components,record['payload'])
                self.ledger = self.intern({'previous':self.ledger,**record,'file':self.pending})
                self.ledger_count += 1
                self.last_event = [event['operation_id'],event['event'],event['durability_checks']['microstep_id'],event['state']]
                self.proved = record['before_snapshot'] if event['event']=='STOP' else record['after_snapshot']
                if event['event']=='STOP':self.terminal='STOP'
                elif event['state'] in ('VERIFIED','ROLLED_BACK') and event['operation_id']=='FINAL':self.terminal=event['state']
                self.pending = None
            return
        if action in ('mkdirat','openat_O_EXCL_NOFOLLOW'):
            assert self.ns.get(path) is None
            token = step['created_token'];contract = self.p['created_identity_contracts'][token]
            self.ns[path] = token
            self.inodes[token] = {k:v for k,v in contract.items() if k!='sha256'}
            self.inodes[token].update(dev=2049,ino=self.ino[token],mode=0o700 if action=='mkdirat' else 0o600,
                                      content=None if action=='mkdirat' else dict(EMPTY))
        elif action=='write_all':
            self.inodes[self.ns[path]]['content'] = dict(self.full_content[step['created_token']])
        elif action=='fchmod_new_fd':
            self.inodes[self.ns[path]]['mode'] = self.p['created_identity_contracts'][self.ns[path]]['mode']
        elif action in ('linkat_flags0','renameat2_NOREPLACE','renameat2_EXCHANGE'):
            src = step['source'];assert self.ns.get(src) is not None
            if action=='renameat2_EXCHANGE':
                assert self.ns.get(path) is not None
                self.ns[src],self.ns[path] = self.ns[path],self.ns[src]
            else:
                assert self.ns.get(path) is None
                if step.get('subject_operation')=='D010':
                    assert not any(t and q.startswith(src+'/') for q,t in self.ns.items())
                self.ns[path] = self.ns[src]
                if action=='renameat2_NOREPLACE':self.ns[src]=None

    def changed_snapshot(self, frame, ns, inodes):
        active = set(ns.values())-{None}
        frame = copy.deepcopy(frame)
        frame['actual_snapshot'] = self.intern({'namespace':self.intern(ns),
            'inodes':self.intern({t:{**inodes[t],'content':self.normalized_content(inodes[t]['content'])} for t in active})})
        return frame

    def partial(self, frame, call, step, record, length):
        result = copy.deepcopy(frame)
        before=(frame['actual_snapshot'],self.canonical_frame(frame)['ledger_files'])
        ns,ins=self.audit.filesystem_view(before)
        require_target_capability(ns,ins,call['path'],'regular_content')
        if record is not None:
            data = self.prefix_bytes[record['event_sha256']][length]
            result['pending_ledger_file']['content'] = {'sha256':hashlib.sha256(data).hexdigest(),
                                                       'length':length,'bytes_hex':data.hex()}
            return result
        # A full-input hash and offset cannot establish the retained prefix hash:
        # different approved buffers can share the same first bytes. Exclude until
        # exact approved bytes are separately bound; never fingerprint slice terms.
        raise UnboundCoverage('Approved partial-write prefix bytes unavailable',{'witness_role':'exact_approved_byte_prefix','path':call['path'],'prefix_length':length})

    def corrupt(self, frame, failure, call):
        assert failure in modes(call['action'],call['role']), 'normatively inapplicable fault'
        before=(frame['actual_snapshot'],self.canonical_frame(frame)['ledger_files'])
        ns,ins=self.audit.filesystem_view(before)
        bound_fault_precheck(call,failure,ns,ins)
        path=call['path'];operations=[]
        controls={'CUSTODY_LOST':'custody_lost','REVOKED':'release_revoked','SERVICE_IDENTITY_CHANGED':'service_replaced','AUTH_CUSTODY_CHANGED':'auth_changed'}
        if failure in controls:
            result=copy.deepcopy(frame);result['persistent_controls'][controls[failure]]=True
            result['_fault_operations']=[];return result
        if failure in ('HEAD_TARGET_INDEX_INCOMPLETE','INDEX_ONLY'):
            raise UnboundCoverage('Exact Git transition witness unavailable',{'witness_role':'exact_git_transition','predicate':failure})
        if call['role']=='graph' and failure in ('CONTENT_HASH_MISMATCH','CORRUPTED_OBJECT','WRONG_TYPE','WRONG_LENGTH','WRONG_SHA1','WRONG_SHA256','TRAILING_ZLIB_BYTES'):
            raise UnboundCoverage('Object-predicate byte witness unavailable',{'witness_role':'approved_git_object_bytes','predicate':failure,'object_source':call['path']})
        if call['role']=='object' and failure in ('WRONG_TYPE','WRONG_LENGTH','WRONG_SHA1','WRONG_SHA256','TRAILING_ZLIB_BYTES'):
            raise UnboundCoverage('Object-predicate byte witness unavailable',{'witness_role':'approved_git_object_bytes','predicate':failure,'object_source':call['path']})
        if failure in ('LEDGER_EVIDENCE_CONTRADICTION','TERMINAL_LEDGER_CONTRADICTION'):
            path=self.root+'/ledger/foreign.json'
        elif failure=='HEAD_INDEX_WORKTREE_CONTRADICTION':path='/opt/aios-src/.git/index'
        elif failure=='TERMINAL_INVARIANT_LOSS':path='/opt/aios-src/.git/HEAD'
        elif failure=='TERMINAL_ALIAS_SPLIT':path=self.p['baseline_alias_groups'][0]['paths'][0]
        elif failure in ('ANCILLARY_MISSING','MISSING_REQUIRED_ALIAS'):
            present=[self.ops[o]['rule']['path'] for o in ('F001','F002','F003') if ns.get(self.ops[o]['rule']['path'])]
            fs_require(present or failure!='ANCILLARY_MISSING','ancillary absence fault has no present ancillary target')
            path=present[0] if present else self.p['baseline_alias_groups'][0]['paths'][0]
        if whole_namespace_call(call) and failure in NAMESPACE_ROLES:
            path=namespace_witness(self.p,ns,ins,failure,call)['concrete_fault_target']
        if not isinstance(path,str) or not path.startswith('/'):
            raise UnboundCoverage('Concrete approved filesystem binding unavailable',
                {'witness_role':{'WRONG_OWNER':'regular_metadata','WRONG_GROUP':'regular_metadata','WRONG_MODE':'regular_metadata','LINK_COUNT_MISMATCH':'regular_hardlink_source','CORRUPTED_OBJECT':'approved_git_object_bytes','SYMLINK_COMPONENT':'regular_symlink_replacement','CONCURRENT_NAMESPACE_REPLACEMENT':'regular_replacement'}.get(failure,'concrete_filesystem_target'),
                 'object_source':path,'predicate':failure,'call_action':call['action']})
        target=concrete_witness(call,failure,path,ns,ins)
        token=ns.get(path);inode=ins.get(token);parent=parent_path(path)
        def fresh(kind,content=None):
            identity=digest({'fault_inode':path,'type':kind})
            t=('LEDGER:' if path.startswith(self.root+'/ledger/') else 'FAULT:')+identity
            dev=ins[ns[parent]]['dev'] if ns.get(parent) in ins else 2049
            return t,{'dev':dev,'ino':200000000000000+int(identity[:12],16),'uid':1000,'gid':1000,
                      'mode':0o700 if kind=='directory' else 0o777 if kind=='symlink' else 0o600,'file_type':kind,
                      'outside_links':2 if kind=='directory' else 0,'content':content}
        if failure in ('CONTENT_HASH_MISMATCH','CORRUPTED_OBJECT','TERMINAL_INVARIANT_LOSS','HEAD_INDEX_WORKTREE_CONTRADICTION'):
            fs_require(inode is not None and inode['file_type']=='regular','content mutation requires existing regular target')
            raw=can({'fixture_corruption':failure,'path':path});h=hashlib.sha256(raw).hexdigest();self.byte_blobs[h]=raw.hex()
            operations=[{'syscall':'ftruncate_write','path':path,'sha256':h}]
        elif failure in ('LEDGER_EVIDENCE_CONTRADICTION','TERMINAL_LEDGER_CONTRADICTION'):
            raw=b'{"foreign_ledger":true}\n';h=hashlib.sha256(raw).hexdigest();self.byte_blobs[h]=raw.hex()
            t,i=fresh('regular',{'sha256':h});operations=[{'syscall':'create_file','path':path,'token':t,'inode':i}]
        elif failure in ('WRONG_OWNER','WRONG_GROUP','WRONG_MODE'):
            fs_require(inode is not None,'metadata mutation target does not exist at this microstep')
            if failure=='WRONG_MODE':operations=[{'syscall':'fchmod','path':path,'mode':0o777}]
            else:operations=[{'syscall':'fchown','path':path,'uid':1001 if failure=='WRONG_OWNER' else inode['uid'],'gid':1001 if failure=='WRONG_GROUP' else inode['gid']}]
        elif failure in ('ANCILLARY_MISSING','MISSING_REQUIRED_ALIAS'):
            operations=[{'syscall':'unlinkat','path':path}]
        elif failure in ('UNEXPECTED_ALIAS','LINK_COUNT_MISMATCH'):
            fs_require(inode is not None,'link fault target absent')
            alias=parent_path(path).rstrip('/')+'/m4-unexpected-'+digest(path)[:12]
            if inode['file_type']=='directory':
                fs_require(failure=='LINK_COUNT_MISMATCH','hardlink to directory is prohibited')
                alias=path.rstrip('/')+'/m4-unexpected-directory'
                t,i=fresh('directory');operations=[{'syscall':'mkdirat','path':alias,'token':t,'inode':i}]
            else:operations=[{'syscall':'linkat','source':path,'path':alias}]
        else:
            fs_require(path!='/','traversal root cannot be replaced')
            if failure not in ('SYMLINK_COMPONENT','WRONG_TYPE','CONCURRENT_NAMESPACE_REPLACEMENT','EEXIST_FOREIGN_ENTRY','UNEXPECTED_PRESENT_ENTRY','EEXIST_FOREIGN_DESTINATION','FOREIGN_EXCHANGE_INODE','SAME_HASH_FOREIGN_INODE','PARENT_REPLACEMENT','TERMINAL_ALIAS_SPLIT'):
                raise ValueError('INVALID_COMPILER_CASE: no bound filesystem fault witness for '+failure)
            if failure=='WRONG_TYPE' and call['action'].startswith('fstat_'):
                raise InvalidFilesystem('held descriptor inode cannot change file type')
            symlink=failure in ('SYMLINK_COMPONENT','WRONG_TYPE')
            kind='symlink' if symlink else inode['file_type'] if inode else 'regular'
            content={'target':'/fixture/foreign-target'} if symlink else copy.deepcopy(inode['content']) if inode else {'sha256':EMPTY['sha256']}
            t,i=fresh(kind,content)
            if inode and not symlink:i.update({k:inode[k] for k in ('uid','gid','mode','outside_links')})
            if inode and inode['file_type']=='directory':
                # Retain the entire old directory tree via a same-device rename,
                # then create the replacement. No child inode disappears.
                retained=parent.rstrip('/')+'/m4-retained-directory-'+digest(path)[:12]
                operations.append({'syscall':'renameat2_NOREPLACE','source':path,'path':retained})
                operations.append({'syscall':{'directory':'mkdirat','symlink':'symlinkat','regular':'create_file'}[kind],'path':path,'token':t,'inode':i})
            elif inode:
                temporary=parent.rstrip('/')+'/m4-fault-source-'+digest(path)[:12]
                operations=[{'syscall':'symlinkat' if symlink else 'create_file','path':temporary,'token':t,'inode':i},
                            {'syscall':'renameat2_REPLACE','source':temporary,'path':path}]
            else:operations=[{'syscall':'symlinkat' if symlink else 'create_file','path':path,'token':t,'inode':i}]
        normal,inodes,ledger=self.audit.checked_transition(before,operations)
        result=self.changed_snapshot(frame,normal,inodes)
        result['ledger_files_override']=pack_files(ledger,self.intern);result['_fault_operations']=operations
        result['_fault_target']=target
        return result

    def exclusion(self, origin, fixture, ordinal, failure, variant, error):
        classification=('UNBOUND_COVERAGE_OBLIGATION' if isinstance(error,UnboundCoverage) else
                        'INVALID_FILESYSTEM_REALIZABILITY' if isinstance(error,InvalidFilesystem) else 'INVALID_COMPILER_CASE')
        row={'origin_fault_site_id':origin,'classification':classification,'reason':str(error) or type(error).__name__}
        if isinstance(error,UnboundCoverage):
            row.update(fixture_id=fixture['id'],call_ordinal=ordinal,failure_mode=failure,outcome_variant=variant,
                       call=dict(fixture['calls'][ordinal-1]),required_binding=error.required_binding,
                       program_sha256=self.program_hash,normative_cursor=fixture['normative_cursor'],
                       operation_id=fixture['operation_id'],microstep_id=fixture['microstep_id'],
                       accepted_coverage=False,filesystem_impossibility=False)
            row['physical_realizability_precheck']=self.audit.unbound_precheck(
                fixture,ordinal,failure,variant,self.normal_prefixes[fixture['id']])
        self.invalid.append(row)

    def candidate(self, fixture, call, ordinal, failure, variant, frame, disposition):
        self.raw += 1
        origin = f"{fixture['id']}:call{ordinal:03d}:{failure}:{variant}"
        try:
            state = self.finish_state(frame,disposition)
            self.audit.validate_outcome(state,fixture)
            self.audit.validate_origin(state,fixture,ordinal,failure,variant,
                                       frame.get('_fault_operations',[]),self.normal_prefixes[fixture['id']],self.byte_blobs,
                                       frame.get('_fault_target'))
            key = digest(state)
            rule = state['required_recovery_action']
        except (AssertionError,ValueError,KeyError,TypeError) as error:
            self.exclusion(origin,fixture,ordinal,failure,variant,error)
            return
        if key in self.states:assert self.states[key]==state,'SHA256 state collision'
        else:self.states[key]=state
        if key not in self.cases:
            self.cases[key]={'id':'C'+key,'semantic_state_fingerprint':key,
                             'required_recovery_action':rule,'normative_rule':RULES[rule],
                             'origin_fault_site_ids':[]}
        self.cases[key]['origin_fault_site_ids'].append(origin)
        self.origins.append({'id':origin,'fixture_id':fixture['id'],'call_ordinal':ordinal,
                             'failure_mode':failure,'outcome_variant':variant,'case_id':'C'+key,
                             'fault_operations':self.intern(frame.get('_fault_operations',[])),
                             'fault_target':frame.get('_fault_target'),
                             'normative_site_id':f"{fixture['direction']}:{fixture['operation_id']}:{fixture['microstep_id']}:call{ordinal:03d}"})

    def fixture(self, direction, oid, mid, calls_, step=None, record=None):
        if direction in ('FORWARD','ROLLBACK'):
            assert self.last_event[:3]==[oid,'BEFORE',mid],('mandatory BEFORE',mid)
            if direction=='ROLLBACK':self.rollback_primitives.add(mid)
        item={'id':f'F{len(self.fixtures)+1:05d}','direction':direction,'operation_id':oid,
              'microstep_id':mid,'step':step['id'] if step else None,'normative_cursor':self.cursor,
              'initial_frame':self.canonical_frame(self.frame()),'last_durable_event':self.last_event,'record':record,'calls':calls_}
        self.audit.validate_frame(item['initial_frame'],item)
        self.fixtures.append(item)
        self.normal_prefixes[item['id']]=self.audit.normal_call_snapshots(item)
        if len(self.fixtures)%100==0:print(json.dumps({'static_compiler_fixtures':len(self.fixtures),'accepted_origins':len(self.origins),'exclusions':len(self.invalid)}),flush=True)
        before = self.frame()
        for i,call in enumerate(calls_,1):
            self.action_counts[call['action'],call['role']] += 1
            self.apply(call,step,record)
            persistent=call['action'] in ('mkdirat','openat_O_EXCL_NOFOLLOW','write_all','fchmod_new_fd','linkat_flags0','renameat2_NOREPLACE','renameat2_EXCHANGE','fsync_parent')
            after=self.frame() if persistent else before
            for failure in modes(call['action'],call['role']):
                if failure.startswith('PARTIAL_WRITE') or failure=='CRASH_DURING_PARTIAL_WRITE':
                    for length in PREFIX_LENGTHS:
                        try:partial=self.partial(before,call,step,record,length)
                        except ValueError as error:
                            self.raw+=1
                            self.exclusion(f"{item['id']}:call{i:03d}:{failure}:prefix-{length}",item,i,failure,f'prefix-{length}',error)
                        else:
                            ns,ins=self.audit.filesystem_view(self.normal_prefixes[item['id']][i-1][0])
                            partial['_fault_target']=concrete_witness(call,failure,call['path'],ns,ins)
                            self.candidate(item,call,i,failure,f'prefix-{length}',partial,'FAILURE')
                elif failure in ('EIO','ENOSPC') and call['action'].startswith('fsync'):
                    for label,frame in [('unchanged',before),('completed',after)]:
                        self.candidate(item,call,i,failure,label,frame,'FAILURE')
                elif failure.startswith('PROCESS_CRASH') or failure.startswith('POWER_LOSS'):
                    frame=after if failure.endswith('AFTER') or failure.endswith('AFTER_DURABILITY') else before
                    self.candidate(item,call,i,failure,'exact-survivor',frame,'RESTART')
                elif failure in ('SHORT_WRITE_THEN_SUCCESS','SHORT_READ_THEN_SUCCESS','EINTR_THEN_SUCCESS'):
                    self.candidate(item,call,i,failure,'completed',after,'SAME_CALL')
                elif failure in ('EACCES','EPERM','ENOSPC','EXDEV','ENOSYS','EINVAL_UNSUPPORTED_FLAGS','EIO','EWOULDBLOCK','EINTR','EBADF'):
                    self.candidate(item,call,i,failure,'unchanged',before,'FAILURE')
                else:
                    cache_key=(digest(before),failure,call['action'],call['path'],call['role'])
                    try:
                        if cache_key not in self.corruption_cache:self.corruption_cache[cache_key]=self.corrupt(before,failure,call)
                        frame=self.corruption_cache[cache_key]
                    except ValueError as error:
                        self.raw+=1
                        self.exclusion(f"{item['id']}:call{i:03d}:{failure}:assigned",item,i,failure,'assigned',error)
                    else:self.candidate(item,call,i,failure,'assigned',frame,'FAILURE')
            before=after

    def ledger_event(self, oid, kind, mid, state, plan=None):
        # Writer observations construct the proposed record; they are NOT durable
        # proof. Only the scanner of surviving accepted records can prove a base.
        if self.proved is None:self.proved=self.snapshot()
        start=self.save();record=self.event(oid,kind,mid,state,plan)
        path=self.root+f'/ledger/{self.ledger_count+1:06d}-{oid}-{kind}.json'
        self.fixture('LEDGER',oid,mid+':'+kind,calls('create_file',None,path),record=record)
        completed=self.save()
        self.restore(start)
        # A persistent external revocation supplies a real STOP predicate. It is
        # a modeled fixture fact, never a new authority or an actual revocation.
        self.controls['release_revoked']=True
        stop=self.event(oid,'STOP','STOP','STOP')
        stop_path=self.root+f'/ledger/{self.ledger_count+1:06d}-{oid}-STOP.json'
        self.fixture('STOP_LEDGER',oid,'STOP_INSTEAD_OF:'+mid+':'+kind,calls('create_file',None,stop_path),record=stop)
        self.restore(completed)
        self.history[oid+':'+kind+':'+mid]=self.save()

    def barrier(self, phase, rollback=False):
        self.fixture('BARRIER_CHECK','ROLLBACK' if rollback else 'FINAL',phase,
            [{'action':'verify_phase_namespace_and_git','path':'/opt/aios-src','role':'full_controlled_namespace_plus_protected_custody'}])
    def build(self):
        for step in self.p['initialization_occurrences']:
            self.cursor = ['INITIALIZATION', step['id']]
            self.fixture('INITIALIZING','PREPARE',step['id'],step['syscall_occurrences'],step=step)
        for index, op in enumerate(self.p['operations']):
            oid, state = op['operation_id'], op['seal_state']
            self.cursor = ['FORWARD', index, 'INTENT']
            self.ledger_event(oid,'INTENT','BEGIN',state)
            for step in op['microsteps']:
                self.cursor = ['FORWARD', index, step['id'], 'BEFORE']
                self.ledger_event(oid,'BEFORE',step['id'],state)
                self.fixture('FORWARD',oid,step['id'],step['syscall_occurrences'],step=step)
                self.cursor = ['FORWARD', index, step['id'], 'AFTER']
                self.ledger_event(oid,'AFTER',step['id'],state)
                if step['stage_checkpoint']:
                    self.ledger_event(oid,'STAGED',step['id'],state)
            self.ledger_event(oid,'DONE','COMPLETE',state)
            if index == len(self.p['operations'])-1 or self.p['operations'][index+1]['seal_state'] != state:
                self.barrier(state)
                self.ledger_event('FINAL','DONE','SEAL:'+state,state)
        self.terminal_fixture('VERIFIED')
        # Replay THREE complete schedules, including both interrupted exchanges.
        # This also covers later primitives under each genuinely distinct prefix.
        steps = self.p['rollback_occurrences']
        for subject in (None, 'M_HEAD', 'M_INDEX'):
            cut = 'FINAL:DONE:SEAL:HEAD_RECONCILED' if subject is None else subject+':AFTER:'+subject+'.002.exchange'
            self.restore(self.history[cut])
            plan = [s['id'] for s in steps if
                    (subject != 'M_INDEX' or s['subject_operation'] != 'M_HEAD') and
                    (not s['id'].endswith('.retain_forward') or s['subject_operation'] == subject)]
            self.cursor = ['ROLLBACK', cut, plan, 0]
            self.ledger_event('ROLLBACK','INTENT','ENTER_ROLLBACK','ROLLBACK_INTENT',plan)
            schedule = [('DONE','BARRIER:ENTER')]
            for owner, phase in zip(('M_HEAD','M_INDEX','F003','F002','F001','D010'),
                                     ('RESTORE_HEAD','RESTORE_INDEX','UNDO_F003','UNDO_F002','UNDO_F001','UNDO_D010')):
                for s in steps:
                    if s['id'] in plan and s['subject_operation'] == owner:
                        schedule.extend((kind,s['id']) for kind in ('BEFORE','AFTER','DONE'))
                schedule.append(('DONE','BARRIER:'+phase))
            schedule += [('DONE','BARRIER:PRE_ROLLBACK_SEAL'),('DONE','SEAL:ROLLED_BACK')]
            lookup = {s['id']:s for s in steps}
            for position, (kind, mid) in enumerate(schedule):
                self.cursor = ['ROLLBACK', cut, plan, position+1]
                if mid.startswith('BARRIER:'):
                    self.barrier(mid.split(':')[1],True)
                if kind == 'AFTER':
                    # The last durable event is REQUIRED to be this step's BEFORE.
                    self.fixture('ROLLBACK','ROLLBACK',mid,lookup[mid]['syscall_occurrences'],step=lookup[mid])
                seal = mid == 'SEAL:ROLLED_BACK'
                self.ledger_event('FINAL' if seal else 'ROLLBACK',kind,mid,
                                  'ROLLED_BACK' if seal else 'ROLLBACK_INTENT')
            self.terminal_fixture('ROLLED_BACK')
        assert self.rollback_primitives == {s['id'] for s in steps}
        return self.output()

    def terminal_fixture(self, state):
        assert self.terminal == state
        self.fixture('TERMINAL','FINAL','POST_TERMINAL:'+state,
                     [{'action':'verify_terminal','path':'/opt/aios-src','role':'terminal_invariants'}])

    def output(self):
        universe=sorted({mode for (action,role) in self.action_counts for mode in modes(action,role)})
        omitted=[]
        for (action,role),count in sorted(self.action_counts.items()):
            excluded=sorted(set(universe)-set(modes(action,role)))
            omitted.append({'action':action,'role':role,'occurrences':count,
                            'failure_classes':excluded,'count':count*len(excluded),
                            'reason':'Failure class is not applicable to this normative syscall and role'})
        inapplicable=sum(x['count'] for x in omitted)
        cases=sorted(self.cases.values(),key=lambda x:x['id'])
        for case in cases:case['origin_fault_site_ids'].sort()
        result={'format':'aios-fault-inventory-v7','status':'PREPARED_NOT_RUN',
                'program_sha256':self.program_hash,'bound_inputs':self.bound_inputs,
                'raw_generated_combinations':self.raw+inapplicable,'raw_applicable_combinations':self.raw,
                'inapplicable_combinations_excluded':inapplicable,
                'invalid_compiler_cases_excluded':sum(x['classification']=='INVALID_COMPILER_CASE' for x in self.invalid),
                'unbound_coverage_obligations':sum(x['classification']=='UNBOUND_COVERAGE_OBLIGATION' for x in self.invalid),
                'exclusion_taxonomy':{'INAPPLICABLE':'not meaningful for syscall/role','INVALID_COMPILER_CASE':'compiler contract/validation failure','INVALID_FILESYSTEM_REALIZABILITY':'witness contradicts actual filesystem/syscall semantics','UNBOUND_COVERAGE_OBLIGATION':'meaningful scenario lacks an approved concrete binding','ACCEPTED':'validated prepared origin; NOT an executed test'},
                'invalid_filesystem_realizability_excluded':sum(x['classification']=='INVALID_FILESYSTEM_REALIZABILITY' for x in self.invalid),
                'semantic_equivalents_removed':len(self.origins)-len(cases),
                'deduplicated_applicable_cases':len(cases),'unique_persistent_semantic_states':len(cases),
                'validated_generated_cases':len(self.origins),'case_count':len(cases),
                'occurrence_count':sum(self.action_counts.values()),
                'inapplicable_combinations':omitted,'candidate_exclusions':self.invalid,
                'outcome_sampling':{'partial_write_prefix_lengths':list(PREFIX_LENGTHS),
                    'power_loss':'Exact fully persisted before/after-call witnesses only; no wildcard persistence sets. Other disk survival patterns require additional explicitly bound cases before adapter acceptance.',
                    'unbound_partial_inputs':'Non-ledger partial writes are UNBOUND_COVERAGE_OBLIGATION until exact approved prefix bytes can be bound. Full-input hash/offset terms are not byte-equivalence keys.'},
                'fixtures':self.fixtures,'origins':self.origins,'cases':cases,'states':self.states,
                'components':self.components,'byte_blobs':self.byte_blobs,'record_catalog':self.records}
        print(json.dumps({'static_compiler_stage':'complete_inventory_audit','origins':len(self.origins),'cases':len(cases)}),flush=True)
        result['independent_validation']=audit_inventory(self.p,result,self.audit)
        return result


class OutcomeAudit:
    """Independent contract checker. Never invokes Compiler or imports03/07.
    Replays full closed evidence payloads and recomputes recovery from state facts.
    """
    def __init__(self, program, components, inputs):
        if not __debug__:raise RuntimeError('Static contract validation requires assertions enabled')
        self.p,self.c,self.inputs=program,components,inputs
        self.program_hash=digest(program)
        self.ledger_cache={None:None}
        self.snapshot_cache=set()
        self.outcome_cache=set()
        self.filesystem_cache=set()
        self.physical_proof_cache={}
        self.physical_prefix_cache={}
        self.catalog={}
        self.files_cache={}
        self.witness_cache={}
        self.view_cache={}
        self.transition_data_cache={}
        self.ops={o['operation_id']:o for o in program['operations']}
        self.steps={s['id']:s for o in program['operations'] for s in o['microsteps']}
        self.steps.update({s['id']:s for s in program['rollback_occurrences']})
        self.forward=[]
        for i,o in enumerate(program['operations']):
            oid,state=o['operation_id'],o['seal_state']
            self.forward.append((oid,'INTENT','BEGIN',state))
            for s in o['microsteps']:
                self.forward.extend((oid,k,s['id'],state) for k in ('BEFORE','AFTER'))
                if s['stage_checkpoint']:self.forward.append((oid,'STAGED',s['id'],state))
            self.forward.append((oid,'DONE','COMPLETE',state))
            if i==len(program['operations'])-1 or program['operations'][i+1]['seal_state']!=state:
                self.forward.append(('FINAL','DONE','SEAL:'+state,state))

    def files(self, root):
        if root not in self.files_cache:
            if len(self.files_cache)>=512:self.files_cache.pop(next(iter(self.files_cache)))
            self.files_cache[root]=files_at(self.c,root)
        return self.files_cache[root]

    def filesystem_view(self, before):
        # Immutable component roots bind this image; replay copies before mutating.
        if before not in self.view_cache:
            if len(self.view_cache)>=8:self.view_cache.pop(next(iter(self.view_cache)))
            self.view_cache[before]=filesystem_view(self.c,before[0],self.files(before[1]))
        return self.view_cache[before]

    def checked_transition(self, before, operations):
        """Independent fault-syscall fold, also used to materialize candidates.
        Only this validator writes the witness cache. Admission still binds the
        resulting candidate to the independently derived normative BEFORE tuple,
        exact operations, fault predicate, evidence contract and recovery class.
        """
        key=(before,digest(operations))
        if key not in self.transition_data_cache:
            ns,ins=self.filesystem_view(before)
            ns,ins=replay_fault_operations(ns,ins,operations)
            declared=self.c[self.c[before[0]]['namespace']]
            value=split_filesystem(ns,ins,declared,self.p['rollback_protocol']['attempt_root']+'/ledger')
            normal,inodes,files=value
            expected=(digest({'namespace':digest(normal),'inodes':digest(inodes)}),pack_files(files,digest))
            if key in self.witness_cache:assert self.witness_cache[key]==expected
            self.witness_cache[key]=expected
            if len(self.transition_data_cache)>=8:self.transition_data_cache.pop(next(iter(self.transition_data_cache)))
            self.transition_data_cache[key]=value
        return self.transition_data_cache[key]

    def snapshot(self, key, proved=False):
        cache=(key,proved)
        if cache in self.snapshot_cache:return
        data=self.c[key];assert set(data)=={'namespace','inodes'}
        ns,bindings=self.c[data['namespace']],self.c[data['inodes']]
        assert set(bindings)==set(ns.values())-{None}
        identities=set()
        for path,token in ns.items():
            assert type(path) is str and path.startswith('/')
            if token is None:continue
            i=bindings[token]
            assert set(i)=={'dev','ino','uid','gid','mode','file_type','outside_links','content'}
            assert all(type(i[k]) is int and i[k]>=0 for k in ('dev','ino','uid','gid','mode','outside_links'))
            assert i['mode']<=0o777 and i['file_type'] in ('regular','directory','symlink')
            content=i['content']
            if i['file_type']=='directory':assert content is None
            elif i['file_type']=='regular':
                assert isinstance(content,dict) and set(content)=={'sha256'}
                assert re.fullmatch('[0-9a-f]{64}',content['sha256'])
            else:assert not proved and set(content)=={'target'}
        for token,i in bindings.items():
            pair=(i['dev'],i['ino']);assert pair not in identities,'unapproved inode sharing';identities.add(pair)
        if proved:
            assert all(i['file_type']!='symlink' for i in bindings.values())
            for group in self.p['baseline_alias_groups']:
                assert sorted(q for q,t in ns.items() if t==group['token'])==group['paths']
                i=bindings[group['token']]
                assert i['outside_links']==0
                assert all(i[k]==v for k,v in group['identity'].items() if k!='sha256')
                assert i['content']['sha256']==group['identity']['sha256']
            for token,i in bindings.items():
                contract=self.p['created_identity_contracts'].get(token)
                if contract:
                    assert all(i[k]==contract[k] for k in ('uid','gid','mode','file_type','outside_links'))
                    if i['file_type']=='regular':
                        assert i['content']==self.c[self.inputs]['full_content'][token]
                        if contract['sha256'] is not None:assert i['content']['sha256']==contract['sha256']
        self.snapshot_cache.add(cache)

    def rollback_sequence(self, plan):
        allowed=[s['id'] for s in self.p['rollback_occurrences']]
        assert len(plan)==len(set(plan)) and all(x in allowed for x in plan)
        assert plan==sorted(plan,key=allowed.index)
        result=[('ROLLBACK','DONE','BARRIER:ENTER','ROLLBACK_INTENT')]
        for subject,phase in zip(('M_HEAD','M_INDEX','F003','F002','F001','D010'),
                                 ('RESTORE_HEAD','RESTORE_INDEX','UNDO_F003','UNDO_F002','UNDO_F001','UNDO_D010')):
            for mid in plan:
                if self.steps[mid]['subject_operation']==subject:
                    result.extend(('ROLLBACK',k,mid,'ROLLBACK_INTENT') for k in ('BEFORE','AFTER','DONE'))
            result.append(('ROLLBACK','DONE','BARRIER:'+phase,'ROLLBACK_INTENT'))
        return result+[('ROLLBACK','DONE','BARRIER:PRE_ROLLBACK_SEAL','ROLLBACK_INTENT'),('FINAL','DONE','SEAL:ROLLED_BACK','ROLLED_BACK')]

    def ledger(self, key):
        if key in self.ledger_cache:return self.ledger_cache[key]
        chain=[];cursor=key
        while cursor not in self.ledger_cache:
            node=self.c[cursor];chain.append((cursor,node));cursor=node['previous']
        prior=self.ledger_cache[cursor]
        for root,node in reversed(chain):
            e=expand_event(self.c,node['payload']);proof=e['durability_checks'];mid=proof['microstep_id']
            assert set(e)==set(self.p['event_contract']['fields'])
            assert set(proof)=={'microstep_id','program_sha256','verified','durable','evidence'}
            assert proof['program_sha256']==self.program_hash and proof['verified'] is True and proof['durable'] is True
            assert e['attempt_root']==self.p['rollback_protocol']['attempt_root']
            assert e['actual_utc']=='2026-09-30T00:00:00.000000Z'
            assert e['ordinal']==(prior['ordinal']+1 if prior else 1)
            assert e['previous_event_sha256']==(prior['event_hash'] if prior else None)
            assert digest(e)==node['event_sha256']
            assert node['file']['content']['sha256']==node['event_sha256']
            assert not prior or prior['terminal'] is None
            before=node['before_snapshot'];after=node['after_snapshot']
            self.snapshot(before,True)
            assert not prior or before==prior['proved'],'evidence snapshot continuity'
            assert e['before_identity']==snapshot_observations(self.c,before)
            assert e['parent_before_identity']=={q:i for q,i in e['before_identity'].items() if i and i['file_type']=='directory'}
            ns=self.c[self.c[before]['namespace']]
            seq=self.forward if prior is None or prior['plan'] is None else self.rollback_sequence(prior['plan'])
            fi=prior['forward'] if prior else 0;ri=prior['reverse'] if prior else 0;plan=prior['plan'] if prior else None
            ev=proof['evidence'];assert set(ev)=={'kind','git_facts','checks','stop_reason','outcome'}
            label={'INTENT':'OPERATION_INTENT','BEFORE':'MICROSTEP_BEFORE','AFTER':'MICROSTEP_AFTER','STAGED':'STAGED_IDENTITY','STOP':'STOP'}.get(e['event'])
            if e['event']=='DONE':
                label='STATE_SEAL' if e['operation_id']=='FINAL' else 'ROLLBACK_BARRIER' if mid.startswith('BARRIER:') else 'ROLLBACK_PRIMITIVE_COMPLETE' if e['operation_id']=='ROLLBACK' else 'OPERATION_COMPLETE'
            assert ev['kind']==label
            path_step=self.steps.get(mid) if e['event'] in ('BEFORE','AFTER','STAGED') or e['operation_id']=='ROLLBACK' and e['event']=='DONE' else None
            assert e['source_path']==(path_step['source'] if path_step else None)
            assert e['destination_path']==(path_step['destination'] if path_step else None)
            event=(e['operation_id'],e['event'],mid,e['state'])
            terminal=None
            if e['event']=='STOP':
                expected=seq[fi if plan is None else ri][0]
                assert e['operation_id'] in (expected,'ROLLBACK')
                assert mid=='STOP' and e['state']=='STOP' and e['source_path'] is None and e['destination_path'] is None
                assert after is None and e['after_identity'] is None and e['parent_after_identity'] is None and e['link_count_changes'] is None
                assert ev=={'kind':'STOP','git_facts':None,'checks':[],'stop_reason':'REVOKED','outcome':'UNKNOWN_RETAIN'}
                proved=before;terminal='STOP'
            else:
                self.snapshot(after,True)
                if event[:3]==('ROLLBACK','INTENT','ENTER_ROLLBACK'):
                    assert plan is None and e['state']=='ROLLBACK_INTENT'
                    assert fi==0 or self.forward[fi][1]!='AFTER','unproved forward effect at rollback entry'
                    plan=node['rollback_plan'];self.rollback_sequence(plan)
                elif plan is None:assert event==seq[fi];fi+=1
                else:assert event==seq[ri];ri+=1
                expected=dict(ns);step=self.steps.get(mid)
                if e['event']=='AFTER':
                    assert step is not None
                    src,dst=step['source'],step['destination'];kind=step['primitive']
                    if kind.startswith('create_'):assert expected[dst] is None;expected[dst]=step['created_token']
                    elif kind=='exchange':assert expected[src] and expected[dst];expected[src],expected[dst]=expected[dst],expected[src]
                    elif kind in ('link','move'):
                        assert expected[src] and expected[dst] is None
                        if kind=='move' and step.get('subject_operation')=='D010':assert not any(t and q.startswith(src+'/') for q,t in expected.items())
                        expected[dst]=expected[src]
                        if kind=='move':expected[src]=None
                assert self.c[self.c[after]['namespace']]==expected
                if e['event']!='AFTER':assert before==after
                assert e['after_identity']==snapshot_observations(self.c,after)
                assert e['parent_after_identity']=={q:i for q,i in e['after_identity'].items() if i and i['file_type']=='directory'}
                assert ev['stop_reason'] is None and ev['outcome']=='PROVEN'
                assert ev['checks']==[ev['kind'],mid,e['state']]
                if e['operation_id']=='FINAL' and e['state'] in self.p['states']:
                    rule=self.p['phase_barriers']['forward'][e['state']]
                    assert expected==rule['namespace'] and ev['git_facts']==rule['git_predicate']
                if mid.startswith('BARRIER:') or mid=='SEAL:ROLLED_BACK':
                    phase=mid.removeprefix('BARRIER:') if mid.startswith('BARRIER:') else 'PRE_ROLLBACK_SEAL'
                    rule=self.p['phase_barriers']['rollback_predicates'][phase]
                    for oid in rule['required_restored_metadata']:
                        assert expected[self.ops[oid]['rule']['path']]=='ORIGINAL:'+oid and expected[self.ops[oid]['rule']['lock_path']] is None
                    for oid in rule['required_absent_ancillary']:assert expected[self.ops[oid]['rule']['path']] is None
                    if rule['documentation_directory_absent']:assert expected[self.ops['D010']['rule']['path']] is None
                    assert ev['git_facts']=={'head_identity':expected['/opt/aios-src/.git/HEAD'],
                        'index_identity':expected['/opt/aios-src/.git/index'],
                        'ancillary_present':[o for o in ('F001','F002','F003') if expected[self.ops[o]['rule']['path']] is not None],
                        'protected_worktree':'UNCHANGED_PR306_OVERLAY',
                        'status_class':'EXACT_ORIGINAL_TWO_ENTRY_DIRTY' if phase=='PRE_ROLLBACK_SEAL' else 'EXACT_REPLAYED_TRANSITIONAL_STATUS'}
                proved=after
                if mid in ('SEAL:VERIFIED','SEAL:ROLLED_BACK'):terminal=mid.split(':')[1]
            op=self.ops.get(e['operation_id'])
            obj={k:op['rule'][k] for k in ('oid','object_type','raw_bytes','raw_sha256')} if op and op['kind']=='object' else None
            assert e['expected_git_oid_if_object']==obj
            proof_ns=self.c[self.c[proved]['namespace']];obs=snapshot_observations(self.c,proved)
            assert e['content_sha256']=={t:obs[q]['sha256'] for q,t in proof_ns.items() if t and obs[q]['file_type']=='regular'}
            if e['event']!='STOP':
                bc={t:e['before_identity'][q]['nlink'] for q,t in ns.items() if t};ac={t:obs[q]['nlink'] for q,t in proof_ns.items() if t}
                assert e['link_count_changes']=={t:{'before':bc.get(t,0),'after':ac.get(t,0)} for t in bc.keys()|ac.keys() if bc.get(t,0)!=ac.get(t,0)}
            prior={'ordinal':e['ordinal'],'event_hash':node['event_sha256'],'proved':proved,'terminal':terminal,
                   'forward':fi,'reverse':ri,'plan':plan,'last_event':list(event)}
            self.ledger_cache[root]=prior
        return prior

    def normal_call_snapshots(self, fixture):
        """Independent syscall-prefix fold; no Compiler.apply/state calls."""
        snap=self.c[fixture['initial_frame']['actual_snapshot']]
        ns=dict(self.c[snap['namespace']]);inodes=copy.deepcopy(self.c[snap['inodes']])
        step=self.steps.get(fixture['step'])
        if step is None:
            step=next((s for s in self.p['initialization_occurrences'] if s['id']==fixture['step']),None)
        current=fixture['initial_frame']['actual_snapshot'];result=[]
        files=dict(self.files(fixture['initial_frame']['ledger_files']))
        file_root=fixture['initial_frame']['ledger_files']
        for call in fixture['calls']:
            before=(current,file_root);a,path=call['action'],call['path'];changed=False
            if fixture['record'] is not None:
                if a=='openat_O_EXCL_NOFOLLOW':files[path]=ledger_file(path,EMPTY['sha256'])
                elif a=='write_all':files[path]['content']={'sha256':fixture['record']['event_sha256']}
                elif a=='fchmod_new_fd':files[path]['mode']=0o600
                if a in ('openat_O_EXCL_NOFOLLOW','write_all','fchmod_new_fd'):file_root=pack_files(files,digest)
            if fixture['record'] is None and step is not None:
                if a in ('mkdirat','openat_O_EXCL_NOFOLLOW'):
                    assert ns.get(path) is None
                    t=step['created_token'];contract=self.p['created_identity_contracts'][t]
                    inode={k:v for k,v in contract.items() if k!='sha256'}
                    inode.update(dev=2049,ino=self.c[self.inputs]['created_inode_numbers'][t],
                                 mode=0o700 if a=='mkdirat' else 0o600,
                                 content=None if a=='mkdirat' else {'sha256':EMPTY['sha256']})
                    inodes[t]=inode;ns[path]=t;changed=True
                elif a=='write_all':
                    inodes[ns[path]]['content']=self.c[self.inputs]['full_content'][step['created_token']];changed=True
                elif a=='fchmod_new_fd':
                    inodes[ns[path]]['mode']=self.p['created_identity_contracts'][ns[path]]['mode'];changed=True
                elif a in ('linkat_flags0','renameat2_NOREPLACE','renameat2_EXCHANGE'):
                    src=step['source'];assert ns.get(src) is not None
                    if a=='renameat2_EXCHANGE':assert ns.get(path) is not None;ns[src],ns[path]=ns[path],ns[src]
                    else:
                        assert ns.get(path) is None;ns[path]=ns[src]
                        if a=='renameat2_NOREPLACE':ns[src]=None
                    changed=True
            if changed:
                active=set(ns.values())-{None}
                current=digest({'namespace':digest(ns),'inodes':digest({t:inodes[t] for t in active})})
            result.append((before,(current,file_root)))
        return result

    def unbound_precheck(self, fixture, ordinal, failure, variant, normal):
        """Retained coverage debt must pass applicability and physical constraints.
        This is conditional realizability, never an approved concrete binding.
        """
        call=fixture['calls'][ordinal-1]
        assert failure in modes(call['action'],call['role'])
        ns,ins=self.filesystem_view(normal[ordinal-1][0])
        facts=bound_fault_precheck(call,failure,ns,ins)
        if variant.startswith('prefix-'):
            assert call['action']=='write_all'
            require_target_capability(ns,ins,call['path'],'regular_content')
            basis='regular write is realizable; exact approved prefix bytes missing'
        elif failure in ('HEAD_TARGET_INDEX_INCOMPLETE','INDEX_ONLY'):
            basis='Git namespace transition is realizable; exact approved transition missing'
        elif call['role']=='graph':
            fs_require(ins.get(ns.get(call['path']),{}).get('file_type')=='directory',
                       'Git graph scope requires a bound directory')
            basis='regular Git object corruption is realizable; approved object bytes missing'
        elif call['role']=='object':
            if isinstance(call['path'],str) and call['path'].startswith('/'):
                require_target_capability(ns,ins,call['path'],'regular_content')
            basis='regular-file fault is realizable; approved object path or bytes missing'
        elif whole_namespace_call(call):
            assert failure in NAMESPACE_ROLES
            basis='namespace fault role is realizable; approved eligible descendant missing'
        else:
            raise AssertionError('unbound obligation lacks a physical realizability contract')
        return {'status':'PASSED_CONDITIONAL_REALIZABILITY','basis':basis,**facts}

    def validate_target(self, before, call, failure, operations, target):
        """Do not use the selector's result as its own acceptance proof.
        Bind the annotation to independent pre-fault objects and actual syscalls.
        """
        assert isinstance(target,dict), 'mutation fault requires a concrete target'
        assert set(target)=={'namespace_scope_anchor','concrete_fault_target','predicate','witness_role'}
        path=target['concrete_fault_target'];scope=target['namespace_scope_anchor']
        whole=whole_namespace_call(call)
        assert target['predicate']==failure
        assert scope==(call['path'] if whole else None)
        ns,ins=self.filesystem_view(before)
        role=NAMESPACE_ROLES[failure] if whole and failure in NAMESPACE_ROLES else TARGET_ROLES[failure]
        assert target['witness_role']==role, 'fault target role mismatch'
        require_target_capability(ns,ins,path,role)
        if whole:
            assert path!=scope, 'scope anchor used as mutation target'
            assert all(op['path']!=scope and op.get('source')!=scope for op in operations), 'scope anchor mutated'
            if failure in NAMESPACE_ROLES:
                assert path.startswith(scope.rstrip('/')+'/')
                assert path in self.p['phase_barriers']['initial_namespace'], 'unapproved namespace witness'
        if operations:
            last=operations[-1]
            actual=(last['source'] if last['syscall']=='linkat' else
                    parent_path(last['path']) if failure=='LINK_COUNT_MISMATCH' and last['syscall']=='mkdirat'
                    else last['path'])
            assert path==actual, 'concrete target differs from mutation syscall'
        else:
            assert failure in ('PARTIAL_WRITE_THEN_EIO','PARTIAL_WRITE_THEN_ENOSPC','CRASH_DURING_PARTIAL_WRITE')
            assert path==call['path']

    def fault_witness(self, before, state, call, failure, operations, target):
        old_snapshot,old_files=before
        ns,ins=self.filesystem_view(before)
        bound_fault_precheck(call,failure,ns,ins)
        controls={'CUSTODY_LOST':'custody_lost','REVOKED':'release_revoked','SERVICE_IDENTITY_CHANGED':'service_replaced','AUTH_CUSTODY_CHANGED':'auth_changed'}
        if failure in controls:
            assert target is None
            assert state['persistent_controls'][controls[failure]] is True and not operations
            assert (state['actual_snapshot'],state['ledger_files'])==before
            return
        assert operations, 'filesystem fault has no syscall witness'
        self.validate_target(before,call,failure,operations,target)
        expected_path=call['path']
        if failure=='HEAD_INDEX_WORKTREE_CONTRADICTION':expected_path='/opt/aios-src/.git/index'
        elif failure=='TERMINAL_INVARIANT_LOSS':expected_path='/opt/aios-src/.git/HEAD'
        elif failure=='TERMINAL_ALIAS_SPLIT':expected_path=self.p['baseline_alias_groups'][0]['paths'][0]
        elif failure in ('LEDGER_EVIDENCE_CONTRADICTION','TERMINAL_LEDGER_CONTRADICTION'):expected_path=self.p['rollback_protocol']['attempt_root']+'/ledger/foreign.json'
        elif failure in ('ANCILLARY_MISSING','MISSING_REQUIRED_ALIAS'):
            old_ns=self.c[self.c[old_snapshot]['namespace']]
            present=[self.ops[o]['rule']['path'] for o in ('F001','F002','F003') if old_ns.get(self.ops[o]['rule']['path'])]
            assert present or failure!='ANCILLARY_MISSING'
            expected_path=present[0] if present else self.p['baseline_alias_groups'][0]['paths'][0]
        whole=whole_namespace_call(call)
        if whole and failure in NAMESPACE_ROLES:
            candidate=operations[-1].get('source') if operations[-1]['syscall']=='linkat' else operations[-1]['path']
            old_ns,old_ins=self.filesystem_view(before)
            assert candidate in self.p['phase_barriers']['initial_namespace']
            assert candidate.startswith(call['path'].rstrip('/')+'/'), 'scope anchor used as mutation target'
            assert old_ns.get(candidate) in old_ins
            required='directory' if failure=='PARENT_REPLACEMENT' else 'regular'
            assert old_ins[old_ns[candidate]]['file_type']==required, 'namespace witness capability mismatch'
            expected_path=candidate
        if failure not in ('UNEXPECTED_ALIAS','LINK_COUNT_MISMATCH'):assert operations[-1]['path']==expected_path,'fault target differs from predicate'
        elif operations[-1]['syscall']=='linkat':assert operations[-1]['source']==expected_path
        else:assert operations[-1]['syscall']=='mkdirat' and parent_path(operations[-1]['path'])==expected_path
        if failure=='WRONG_TYPE' and call['action'].startswith('fstat_'):
            raise InvalidFilesystem('held descriptor inode cannot change file type')
        witness=(before,digest(operations))
        if witness not in self.witness_cache:self.checked_transition(before,operations)
        fs_require((state['actual_snapshot'],state['ledger_files'])==self.witness_cache[witness],'fault syscall witness mismatch')
        last=operations[-1]
        if failure=='WRONG_MODE':assert operations[0]['syscall']=='fchmod' and operations[0]['mode']==0o777
        elif failure in ('WRONG_OWNER','WRONG_GROUP'):
            assert operations[0]['syscall']=='fchown' and operations[0]['uid' if failure=='WRONG_OWNER' else 'gid']==1001
        elif failure in ('SYMLINK_COMPONENT','WRONG_TYPE'):assert any(x['syscall']=='symlinkat' for x in operations)
        elif failure in ('CONTENT_HASH_MISMATCH','CORRUPTED_OBJECT','TERMINAL_INVARIANT_LOSS','HEAD_INDEX_WORKTREE_CONTRADICTION'):assert last['syscall']=='ftruncate_write'

    def validate_origin(self, state, fixture, ordinal, failure, variant, operations, normal, blobs, target=None):
        """Acceptance gate: independent prefix, transition and recovery checks.
        Called for EVERY candidate before global state insertion/deduplication.
        """
        call=fixture['calls'][ordinal-1]
        assert failure in modes(call['action'],call['role'])
        before,after=normal[ordinal-1]
        if variant=='assigned':self.fault_witness(before,state,call,failure,operations,target)
        elif variant in ('unchanged','completed','exact-survivor'):
            completed=variant=='completed' or failure in ('PROCESS_CRASH_AFTER','POWER_LOSS_AFTER_DURABILITY')
            fs_require((state['actual_snapshot'],state['ledger_files'])==(after if completed else before),
                       'outcome is not produced by the specified syscall prefix')
            assert not operations
            assert target is None, 'nonmutation fault has a mutation target'
        else:
            assert variant.startswith('prefix-') and call['action']=='write_all' and fixture['record'] is not None
            length=int(variant.split('-')[1]);assert length in PREFIX_LENGTHS
            prefix=can(expand_event(self.c,fixture['record']['payload']))[:length]
            expected=hashlib.sha256(prefix).hexdigest()
            files=copy.deepcopy(self.files(before[1]))
            fs_require(call['path'] in files and files[call['path']]['file_type']=='regular','partial write target absent or not regular')
            files[call['path']]['content']={'sha256':expected}
            fs_require((state['actual_snapshot'],state['ledger_files'])==(before[0],pack_files(files,digest)),
                       'partial write invented a namespace or unrelated content change')
            assert blobs[expected]==prefix.hex() and not operations
            self.validate_target(before,call,failure,[],target)
        self.validate_frame(state,fixture if fixture['direction'] in ('FORWARD','ROLLBACK') else None)
        assert state['required_recovery_action']==independent_recovery(state,failure)

    def validate_frame(self, frame, fixture=None):
        self.snapshot(frame['actual_snapshot'])
        files=self.files(frame['ledger_files'])
        fk=(frame['actual_snapshot'],frame['ledger_files'])
        if fk not in self.filesystem_cache:
            ns,ins=self.filesystem_view(fk)
            validate_filesystem(ns,ins)
            counts=collections.Counter(t for t in ns.values() if t is not None)
            for path,f in files.items():
                assert set(f)=={'path','inode_identity','dev','ino','uid','gid','mode','file_type','nlink','content'}
                assert f['path']==path and path.startswith(self.p['rollback_protocol']['attempt_root']+'/ledger/')
                assert f['nlink']==(2+sum(1 for q,t in ns.items() if t and parent_path(q)==path and ins[t]['file_type']=='directory') if f['file_type']=='directory' else counts['LEDGER:'+f['inode_identity']])
            self.filesystem_cache.add(fk)
        # Independently recover the proved prefix from the physical files. No
        # pending/committed flag, call position, direction or compiler root is read.
        proof=frame['durable_proof_state'];external=frame.get('external_baseline_witness')
        external_base=external_baseline_snapshot(self.c,external,self.c[self.inputs]['external_baseline_bindings'],self.program_hash,self.p['rollback_protocol']['attempt_root'])
        pk=(frame['ledger_files'],external)
        if pk not in self.physical_proof_cache:
            root=None;proved=external_base;terminal=None;count=0;rejection=None;last_sha=None
            for block in self.c[frame['ledger_files']]['file_blocks']:
                incoming=(root,proved,block)
                if terminal is not None:rejection='FILE_AFTER_TERMINAL';break
                if incoming in self.physical_prefix_cache:
                    root,proved,terminal,count,last_sha=self.physical_prefix_cache[incoming]
                    continue
                for leaf in self.c[block]:
                    f=self.c[leaf];path=f['path'];sha=(f['content'] or {}).get('sha256');record=self.catalog.get(sha)
                    if terminal is not None:rejection='FILE_AFTER_TERMINAL';break
                    expected_identity=hashlib.sha256(can({'ledger_inode':path})).hexdigest()
                    if f['file_type']!='regular' or [f[k] for k in ('uid','gid','mode','nlink')]!=[1000,1000,0o600,1] or f['inode_identity']!=expected_identity or f['dev']!=2049 or f['ino']!=10000000000+int(expected_identity[:12],16):
                        rejection='UNTRUSTED_FILE_METADATA';break
                    if record is None:rejection='PARTIAL_OR_MALFORMED_BYTES';break
                    e=expand_event(self.c,record['payload']);ordinal=count+1
                    if Path(path).name!=f"{ordinal:06d}-{e['operation_id']}-{e['event']}.json" or e['ordinal']!=ordinal or e['previous_event_sha256']!=last_sha:
                        rejection='FILENAME_OR_CHAIN_MISMATCH';break
                    if count==0 and proved is None:proved=record['before_snapshot']
                    if record['before_snapshot']!=proved:rejection='PROOF_CONTINUITY_MISMATCH';break
                    root=digest({'previous':root,**record,'file':f});last_sha=sha;count+=1
                    proved=record['before_snapshot'] if e['event']=='STOP' else record['after_snapshot']
                    if e['event']=='STOP':terminal='STOP'
                    elif e['operation_id']=='FINAL' and e['state'] in ('VERIFIED','ROLLED_BACK'):terminal=e['state']
                if rejection:break
                self.physical_prefix_cache[incoming]=(root,proved,terminal,count,last_sha)
            base=external_base
            if count and base is None:
                first=self.c[self.c[self.c[frame['ledger_files']]['file_blocks'][0]][0]]
                base=self.catalog[first['content']['sha256']]['before_snapshot']
            self.physical_proof_cache[pk]=(root,proved,terminal,{'base_snapshot':base,'source':'LEDGER' if count else 'EXTERNAL_BASELINE' if external_base is not None else 'NONE','accepted_record_count':count,'rejection':rejection})
        root,proved,terminal,expected=self.physical_proof_cache[pk]
        assert (frame['ledger_root'],frame['last_proved_snapshot'],frame['terminal'],proof)==(root,proved,terminal,expected)
        history=self.ledger(root)
        if history:assert history['proved']==proved and history['terminal']==terminal
        if proved:self.snapshot(proved,True)
        # BEFORE is mandatory in the starting fixture. A witnessed later fault
        # may remove/replace ledger files; its surviving prefix may be shorter.
        # Full origin replay separately proves that loss follows the valid start.
        if fixture and fixture['direction'] in ('FORWARD','ROLLBACK') and proof['rejection'] is None and frame['ledger_files']==fixture['initial_frame']['ledger_files']:
            assert history and history['last_event'][:3]==[fixture['operation_id'],'BEFORE',fixture['step']]
        return history

    def validate_outcome(self, state, fixture=None):
        assert set(state)=={'ledger_root','last_proved_snapshot','actual_snapshot','external_baseline_witness',
                            'ledger_files','durable_proof_state','persistent_controls','terminal','format',
                            'uncertainty_class','required_recovery_action','observed_or_possible_unproved_effects','git'}, 'nonsemantic state annotation'
        assert state['format']=='aios-persistent-state-v7'
        key=digest(state)
        if key in self.outcome_cache:return
        self.validate_frame(state,fixture)
        actual,proved=state['actual_snapshot'],state['last_proved_snapshot']
        delta=actual!=proved;rejection=state['durable_proof_state']['rejection']
        if rejection:
            expected='STOP_TORN_RECORD' if rejection=='PARTIAL_OR_MALFORMED_BYTES' else 'STOP_RECOVERY_REQUIRED'
            uncertainty='UNTRUSTED_LEDGER'
        elif state['uncertainty_class']=='LIVE_CALL_CONTINUATION':
            assert not any(state['persistent_controls'].values()) and state['terminal'] is None
            expected,uncertainty='CONTINUE_SAME_CALL','LIVE_CALL_CONTINUATION'
        elif state['terminal']=='STOP' or any(state['persistent_controls'].values()):
            expected='STOP_AMBIGUOUS_EFFECT' if delta else 'STOP_PRESERVE';uncertainty='UNPROVED_EFFECT' if delta else 'NONE'
        elif proved is None or state['terminal'] is not None and delta:
            expected,uncertainty='STOP_RECOVERY_REQUIRED','RECOVERY_AUTHORITY_REQUIRED'
        elif delta:expected,uncertainty='STOP_AMBIGUOUS_EFFECT','UNPROVED_EFFECT'
        elif state['uncertainty_class']=='KNOWN_FAILURE':expected,uncertainty='STOP_PRESERVE','KNOWN_FAILURE'
        elif state['terminal']:expected,uncertainty='TERMINAL_INSPECTION_ONLY','NONE'
        else:expected,uncertainty='CONTINUE_PROVED_PREFIX','NONE'
        assert (state['required_recovery_action'],state['uncertainty_class'])==(expected,uncertainty)
        assert state['observed_or_possible_unproved_effects']==(None if not delta else {'classification':'UNKNOWN_TO_EVIDENCE','actual_snapshot':actual})
        snap=self.c[actual];ns=self.c[snap['namespace']]
        assert state['git']=={'HEAD':ns.get('/opt/aios-src/.git/HEAD'),'index':ns.get('/opt/aios-src/.git/index'),
                             'worktree_namespace':snap['namespace'],'content_identities':snap['inodes']}
        self.outcome_cache.add(key)


def independent_recovery(state, failure_mode):
    """Protocol recovery, from independently scanned durable proof and disposition."""
    rejection=state['durable_proof_state']['rejection']
    if rejection:return 'STOP_TORN_RECORD' if rejection=='PARTIAL_OR_MALFORMED_BYTES' else 'STOP_RECOVERY_REQUIRED'
    success=failure_mode in ('SHORT_WRITE_THEN_SUCCESS','SHORT_READ_THEN_SUCCESS','EINTR_THEN_SUCCESS')
    if success and not any(state['persistent_controls'].values()) and state['terminal'] is None:return 'CONTINUE_SAME_CALL'
    changed=state['actual_snapshot']!=state['last_proved_snapshot']
    if state['terminal']=='STOP' or any(state['persistent_controls'].values()):return 'STOP_AMBIGUOUS_EFFECT' if changed else 'STOP_PRESERVE'
    if state['last_proved_snapshot'] is None or state['terminal'] and changed:return 'STOP_RECOVERY_REQUIRED'
    if changed:return 'STOP_AMBIGUOUS_EFFECT'
    restart=failure_mode.startswith('PROCESS_CRASH') or failure_mode.startswith('POWER_LOSS')
    if not success and not restart:return 'STOP_PRESERVE'
    if state['terminal']:return 'TERMINAL_INSPECTION_ONLY'
    return 'CONTINUE_PROVED_PREFIX'


def audit_inventory(program, inventory, checker=None, progress=None):
    """Independent static audit, not tests. Immutable pre-acceptance proofs may
    be reused only after rehashing every component. A standalone call builds a
    fresh independent checker. Compiler methods are never used for validation.
    """
    components=inventory['components'];states=inventory['states']
    for key,encoded in inventory['byte_blobs'].items():assert hashlib.sha256(bytes.fromhex(encoded)).hexdigest()==key
    for index,(key,value) in enumerate(components.items(),1):
        assert key==digest(value),'component hash'
        if progress and index%50000==0:progress('components_rehashed',index)
    if checker is None:checker=OutcomeAudit(program,components,inventory['bound_inputs'])
    else:assert checker.c is components and checker.p==program and checker.inputs==inventory['bound_inputs']
    checker.catalog=inventory['record_catalog']
    fixtures={f['id']:f for f in inventory['fixtures']}
    for f in fixtures.values():checker.validate_frame(f['initial_frame'],f)
    by_case={c['id']:c for c in inventory['cases']}
    assert len(by_case)==len(inventory['cases'])
    for index,(key,state) in enumerate(states.items(),1):
        if progress and index%25000==0:progress('states_validated',index)
        assert key==digest(state)==digest(dict(reversed(list(state.items()))))
        checker.validate_outcome(state)
        assert 'C'+key in by_case
        assert by_case['C'+key]['normative_rule']==RULES[state['required_recovery_action']]
    origins={o['id']:o for o in inventory['origins']};assert len(origins)==len(inventory['origins'])
    physical_proofs={};semantic_groups={}
    for key,state in states.items():
        physical=(state['actual_snapshot'],state['ledger_files'],state.get('external_baseline_witness'),digest(state['persistent_controls']))
        proof=tuple(state[k] if k!='durable_proof_state' else digest(state[k]) for k in ('ledger_root','last_proved_snapshot','terminal','durable_proof_state'))
        assert physical_proofs.setdefault(physical,proof)==proof, 'unjustified physical-state proof split'
        semantic=physical+(state['uncertainty_class'],state['required_recovery_action'])
        assert semantic_groups.setdefault(semantic,key)==key, 'unjustified persistent semantic fingerprint split'
    seen=set()
    for case in by_case.values():
        assert case['origin_fault_site_ids']
        for key in case['origin_fault_site_ids']:
            assert key not in seen and origins[key]['case_id']==case['id'];seen.add(key)
    assert seen==set(origins)
    normal={f['id']:checker.normal_call_snapshots(f) for f in fixtures.values()}
    for index,o in enumerate(origins.values(),1):
        if progress and index%50000==0:progress('origins_validated',index)
        f=fixtures[o['fixture_id']];call=f['calls'][o['call_ordinal']-1]
        assert o['failure_mode'] in modes(call['action'],call['role'])
        state=states[by_case[o['case_id']]['semantic_state_fingerprint']]
        if o['outcome_variant']=='assigned' and whole_namespace_call(call) and o['failure_mode'] in NAMESPACE_ROLES:
            normal_ns,normal_ins=checker.filesystem_view(normal[f['id']][o['call_ordinal']-1][0])
            assert o['fault_target']==namespace_witness(program,normal_ns,normal_ins,o['failure_mode'],call)
        checker.validate_origin(state,f,o['call_ordinal'],o['failure_mode'],o['outcome_variant'],
                                components[o['fault_operations']],normal[f['id']],inventory['byte_blobs'],o['fault_target'])
        if f['initial_frame']['persistent_controls']['release_revoked']:
            assert state['required_recovery_action'].startswith('STOP_')
        # Directly bind the no-effect read/errno outcome to its required class;
        # classify all halted outcomes first so STOP never inherits success logic.
        if not state['required_recovery_action'].startswith('STOP_') and not state['terminal']:
            success=o['failure_mode'] in ('SHORT_WRITE_THEN_SUCCESS','SHORT_READ_THEN_SUCCESS','EINTR_THEN_SUCCESS')
            assert state['required_recovery_action']==('CONTINUE_SAME_CALL' if success else 'CONTINUE_PROVED_PREFIX')
    excluded={e['origin_fault_site_id']:e for e in inventory['candidate_exclusions']}
    assert len(excluded)==len(inventory['candidate_exclusions']) and not set(excluded)&set(origins)
    expected=set();actions=collections.Counter()
    for f in fixtures.values():
        for i,call in enumerate(f['calls'],1):
            actions[call['action'],call['role']]+=1
            for mode in modes(call['action'],call['role']):
                variants=(['prefix-1','prefix-2'] if mode.startswith('PARTIAL_WRITE') or mode=='CRASH_DURING_PARTIAL_WRITE' else
                          ['unchanged','completed'] if mode in ('EIO','ENOSPC') and call['action'].startswith('fsync') else
                          ['exact-survivor'] if mode.startswith(('PROCESS_CRASH','POWER_LOSS')) else
                          ['completed'] if mode in ('SHORT_WRITE_THEN_SUCCESS','SHORT_READ_THEN_SUCCESS','EINTR_THEN_SUCCESS') else
                          ['unchanged'] if mode in ('EACCES','EPERM','ENOSPC','EXDEV','ENOSYS','EINVAL_UNSUPPORTED_FLAGS','EIO','EWOULDBLOCK','EINTR','EBADF') else ['assigned'])
                for variant in variants:expected.add(f"{f['id']}:call{i:03d}:{mode}:{variant}")
    assert expected==set(origins)|set(excluded), 'missing/extra candidate origin'
    universe={v for a,r in actions for v in modes(a,r)}
    assert sum(n*len(universe-set(modes(a,r))) for (a,r),n in actions.items())==inventory['inapplicable_combinations_excluded']
    for e in excluded.values():
        assert e['reason']
        if e['classification']=='UNBOUND_COVERAGE_OBLIGATION':
            assert e['required_binding'] and e['accepted_coverage'] is False and e['filesystem_impossibility'] is False
            assert e['program_sha256']==inventory['program_sha256'] and e['fixture_id'] in fixtures
            f=fixtures[e['fixture_id']]
            assert e['physical_realizability_precheck']==checker.unbound_precheck(
                f,e['call_ordinal'],e['failure_mode'],e['outcome_variant'],normal[f['id']])
    for kind,field in [('INVALID_COMPILER_CASE','invalid_compiler_cases_excluded'),('INVALID_FILESYSTEM_REALIZABILITY','invalid_filesystem_realizability_excluded'),('UNBOUND_COVERAGE_OBLIGATION','unbound_coverage_obligations')]:
        assert sum(e['classification']==kind for e in excluded.values())==inventory[field]
    assert inventory['raw_applicable_combinations']==len(origins)+len(excluded)
    assert inventory['semantic_equivalents_removed']==len(origins)-len(by_case)
    assert inventory['raw_generated_combinations']-inventory['inapplicable_combinations_excluded']-inventory['invalid_compiler_cases_excluded']-inventory['invalid_filesystem_realizability_excluded']-inventory['unbound_coverage_obligations']-inventory['semantic_equivalents_removed']==len(by_case)
    assert len(states)==len(by_case)==inventory['unique_persistent_semantic_states']
    return {'status':'PASS_STATIC_ONLY','generated_outcomes_checked':len(origins),
            'surviving_cases_checked':len(by_case),'evidence_chains_checked':len(checker.ledger_cache)-1,
            'fixtures_checked':len(fixtures),'physical_proof_groups_checked':len(physical_proofs),
            'global_semantic_groups_checked':len(semantic_groups),'tests_executed':False}


def main():
    if not __debug__:raise RuntimeError('Static validation cannot run under -O')
    program=json.loads((P/'01_OPERATION_PROGRAM.json').read_bytes())
    result=Compiler(program).build()
    with (P/'06_FAULT_CASES.json').open('w',encoding='utf-8',newline='\n') as output:
        json.dump(result,output,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
        output.write('\n')
    print(json.dumps({k:v for k,v in result.items() if isinstance(v,int) or k=='independent_validation'},sort_keys=True))


if __name__=='__main__':
    main()
